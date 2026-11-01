/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license: https://github.com/azerothcore/azerothcore-wotlk/blob/master/LICENSE-AGPL3
 */

#include "ScriptMgr.h"
#include "Player.h"
#include "Config.h"
#include "Chat.h"
#include "ScriptedGossip.h"
#include "IndividualProgression.h"
#include "CharacterServicesMoneyPolicy.h"
#include "CharacterServicesGatePolicy.h"

class CharacterServices : public CreatureScript
{
  public:
    CharacterServices() : CreatureScript("character_services") { }

    // The vendor can still compile with historical IP without the paid API.
    // In that mode passage is not offered, and an explicitly configured
    // paid gate must deny generic tier sales instead of bypassing it.
#if defined(COSMIC_IP_PAID_EXPANSION_API_VERSION) && COSMIC_IP_PAID_EXPANSION_API_VERSION == 1
    using ExpansionEra = IndividualProgressionExpansionPolicy::Era;
    using ExpansionResult = IndividualProgressionExpansionPolicy::PurchaseResult;

    // Config prices are in gold; the IP API receives COPPER and internally
    // debits a signed 32-bit value. Reject overflow and accidental free offers.
    static bool GetExpansionCostCopper(ExpansionEra era, uint32& copper)
    {
      char const* key = era == ExpansionEra::Tbc
        ? "CharacterServices.ExpansionUnlock.Cost.VanillaToTBC"
        : "CharacterServices.ExpansionUnlock.Cost.TBCToWotLK";
      uint32 const fallbackGold = era == ExpansionEra::Tbc ? 1000u : 3000u;
      uint32 const gold = sConfigMgr->GetOption<uint32>(key, fallbackGold);
      return CharacterServicesMoneyPolicy::TryGoldToCopper(gold, false, copper);
    }
#endif

    static bool CanOfferProgressionTier(Player* player, uint8 nextTier)
    {
#if defined(COSMIC_IP_PAID_EXPANSION_API_VERSION) && COSMIC_IP_PAID_EXPANSION_API_VERSION == 1
      bool const ipPaidActive = sIndividualProgression->IsPaidExpansionActive();
      uint8 const effectiveCeiling = ipPaidActive
        ? sIndividualProgression->GetMaxServiceGrantableStage(player) : 0u;
      return CharacterServicesGatePolicy::CanOfferGenericTier(
          sConfigMgr->GetOption<bool>("CharacterServices.ExpansionUnlock.Enable", false),
          ipPaidActive, nextTier, effectiveCeiling);
#else
      (void)player;
      (void)nextTier;
      // If a vendor config requests paid expansion under old IP, fail closed
      // instead of allowing legacy generic tier sales to cross the era.
      return !sConfigMgr->GetOption<bool>("CharacterServices.ExpansionUnlock.Enable", false);
#endif
    }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
      if (!sConfigMgr->GetOption<bool>("CharacterServices.Enable", false))
       return false;

      if (!player || !player->GetSession())
          return false;

      if (player->HasAtLoginFlag(AT_LOGIN_RENAME) || player->HasAtLoginFlag(AT_LOGIN_CUSTOMIZE) || player->HasAtLoginFlag(AT_LOGIN_CHANGE_RACE) || player->HasAtLoginFlag(AT_LOGIN_CHANGE_FACTION))
      {
        ChatHandler(player->GetSession()).PSendSysMessage("You already have a pending service. Please log out to use it.");
        CloseGossipMenuFor(player);
        return false;
      }

      if (sConfigMgr->GetOption<bool>("CharacterServices.NameChange.Enable", false))
        AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "|TInterface/Icons/inv_misc_note_02:50:50|tChange My Name", GOSSIP_SENDER_MAIN, 1, "Confirm Name Change.", GetServiceCost(player, 1), false);
      if (sConfigMgr->GetOption<bool>("CharacterServices.AppearanceChange.Enable", false))
        AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "|TInterface/Icons/ability_rogue_disguise:50:50|tChange My Appearance", GOSSIP_SENDER_MAIN, 2, "Confirm Appearance Change.", GetServiceCost(player, 2), false);
      if (sConfigMgr->GetOption<bool>("CharacterServices.RaceChange.Enable", false))
        AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "|TInterface/Icons/inv_misc_grouplooking:50:50|tChange My Race", GOSSIP_SENDER_MAIN, 3, "Confirm Race Change.", GetServiceCost(player, 3), false);
      if (sConfigMgr->GetOption<bool>("CharacterServices.FactionChange.Enable", false))
        AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "|TInterface/Icons/inv_bannerpvp_03:50:50|tChange My Faction", GOSSIP_SENDER_MAIN, 4, "Confirm Faction Change.", GetServiceCost(player, 4), false);
      
#if defined(COSMIC_IP_PAID_EXPANSION_API_VERSION) && COSMIC_IP_PAID_EXPANSION_API_VERSION == 1
      // The owner must BOTH complete the prior era AND pay Vezrath.
      // The IP entitlement module performs the eligibility and money checks.
      // This source requires IP's DRAFT paid-expansion API, default OFF.
      if (sConfigMgr->GetOption<bool>("CharacterServices.ExpansionUnlock.Enable", false) &&
          sIndividualProgression->IsPaidExpansionActive())
      {
        uint32 copper = 0;
        if (GetExpansionCostCopper(ExpansionEra::Tbc, copper))
        {
          ExpansionResult const result = sIndividualProgression->CanPurchaseExpansion(
              player, static_cast<uint8>(ExpansionEra::Tbc), copper);
          if (result == ExpansionResult::Success || result == ExpansionResult::InsufficientFunds)
            AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1,
                "|TInterface/Icons/achievement_dungeon_karazhan:50:50|tUnlock The Burning Crusade",
                GOSSIP_SENDER_MAIN, 200,
                "Confirm TBC passage for " + std::to_string(copper / 10000) + " gold. IP will handle the payment.",
                0u, false);
        }
        if (GetExpansionCostCopper(ExpansionEra::Wrath, copper))
        {
          ExpansionResult const result = sIndividualProgression->CanPurchaseExpansion(
              player, static_cast<uint8>(ExpansionEra::Wrath), copper);
          if (result == ExpansionResult::Success || result == ExpansionResult::InsufficientFunds)
            AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1,
                "|TInterface/Icons/achievement_boss_kelthuzad_01:50:50|tUnlock Wrath of the Lich King",
                GOSSIP_SENDER_MAIN, 201,
                "Confirm Wrath passage for " + std::to_string(copper / 10000) + " gold. IP will handle the payment.",
                0u, false);
        }
      }

#endif
      // Add progression tier purchase option if enabled
      if (sConfigMgr->GetOption<bool>("CharacterServices.ProgressionTier.Enable", false))
      {
        uint8 currentTier = sIndividualProgression->GetPlayerProgressionFromQuests(player);
        uint8 maxAllowedTier = sConfigMgr->GetOption<uint8>("CharacterServices.ProgressionTier.MaxApplicableTier", 0);
        bool requireAccountUnlock = sConfigMgr->GetOption<bool>("CharacterServices.ProgressionTier.RequireAccountUnlock", true);

        // When RequireAccountUnlock is true (default), the ceiling is the account's
        // highest achieved tier. When false, any character may buy up to the top tier
        // without another character having unlocked it first.
        uint8 accountMaxTier = requireAccountUnlock
          ? sIndividualProgression->GetAccountProgression(player->GetSession()->GetAccountId())
          : PROGRESSION_WOTLK_TIER_5;

        // If MaxApplicableTier is set (non-zero), use it as a cap on the account's max tier
        if (maxAllowedTier > 0 && accountMaxTier > maxAllowedTier)
          accountMaxTier = maxAllowedTier;

        uint8 nextTier = GetNextProgressionTier(currentTier);

        // Only offer if the account has unlocked the next tier and the player is not at max progression
        if (currentTier < PROGRESSION_WOTLK_TIER_5 && nextTier <= accountMaxTier &&
            CanOfferProgressionTier(player, nextTier))
        {
          std::string nextTierName = GetProgressionTierName(nextTier);
          std::string tierIcon = GetTierIcon(nextTier);

          uint32 tierCostCopper = 0;
          if (TryGetProgressionTierCost(nextTier, tierCostCopper))
            AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1,
              "|T" + tierIcon + ":50:50|tProgress to " + nextTierName,
              GOSSIP_SENDER_MAIN, 100 + nextTier, // Use 100 + tier as the action ID
              "Purchase progression to: " + nextTierName + " for " +
                  std::to_string(tierCostCopper / 10000) + " gold. The service will charge on success.",
              0u, false);
          // Invalid/overflowed configured tier price: no purchasable offer.
        }
        else if (currentTier < PROGRESSION_WOTLK_TIER_5) // Not at max, but nothing unlocked to buy yet
        {
          ChatHandler(player->GetSession()).PSendSysMessage("Your account has not unlocked a higher progression tier yet. Progress further on another character to unlock it here.");
        }
      }

      SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());

      return true;
    }

    bool OnGossipSelect(Player* player, Creature* /*creature*/, uint32 sender, uint32 action) override
    {
      if (!player || !player->GetSession())
          return false;

      ClearGossipMenuFor(player);
      if (sender != GOSSIP_SENDER_MAIN ||
          !sConfigMgr->GetOption<bool>("CharacterServices.Enable", false))
      {
        CloseGossipMenuFor(player);
        return false;
      }

#if defined(COSMIC_IP_PAID_EXPANSION_API_VERSION) && COSMIC_IP_PAID_EXPANSION_API_VERSION == 1
      // Expansion passage: ALWAYS delegate eligibility, debit and durable
      // entitlement to IP. Never grant Wrath first-raid completion (stage 14).
      if (action == 200 || action == 201)
      {
        if (!sConfigMgr->GetOption<bool>("CharacterServices.ExpansionUnlock.Enable", false) ||
            !sIndividualProgression->IsPaidExpansionActive())
        {
          CloseGossipMenuFor(player);
          return false;
        }
        ExpansionEra const era = action == 200 ? ExpansionEra::Tbc : ExpansionEra::Wrath;
        uint32 copper = 0;
        if (!GetExpansionCostCopper(era, copper))
        {
          ChatHandler(player->GetSession()).PSendSysMessage("Expansion access is temporarily unavailable due to an invalid service price.");
          CloseGossipMenuFor(player);
          return false;
        }

        ExpansionResult const purchased = sIndividualProgression->PurchaseExpansion(
            player, static_cast<uint8>(era), copper);
        if (purchased == ExpansionResult::Success)
        {
          sIndividualProgression->checkIPPhasing(player, player->GetAreaId());
          ChatHandler(player->GetSession()).PSendSysMessage("Expansion access purchased successfully.");
        }
        else if (purchased == ExpansionResult::InsufficientFunds)
          ChatHandler(player->GetSession()).PSendSysMessage("You do not have enough gold for this expansion.");
        else if (purchased == ExpansionResult::AlreadyOwned)
          ChatHandler(player->GetSession()).PSendSysMessage("You already own this expansion's access.");
        else if (purchased == ExpansionResult::EntryUnavailable)
          ChatHandler(player->GetSession()).PSendSysMessage("This purchase could not be completed. Check your gold and contact server staff if the balance changed.");
        else if (purchased == ExpansionResult::FeatureInactive)
          ChatHandler(player->GetSession()).PSendSysMessage("The expansion purchase service is unavailable. No purchase was processed.");
        else if (purchased == ExpansionResult::BlockedByProgressionLimit)
          ChatHandler(player->GetSession()).PSendSysMessage("This expansion is not yet available on the server.");
        else
          ChatHandler(player->GetSession()).PSendSysMessage("You have not yet met the final progression requirements for this expansion.");
        CloseGossipMenuFor(player);
        return purchased == ExpansionResult::Success;
      }

#else
      // Historical IP lacks durable entitlement/payment API. Always deny
      // forged passage selection; never fall back to ForceUpdate(8/14).
      if (action == 200 || action == 201)
      {
        CloseGossipMenuFor(player);
        return false;
      }
#endif
      // Handle progression tier purchases (action IDs 100+)
      if (action >= 100)
      {
        if (!sConfigMgr->GetOption<bool>("CharacterServices.ProgressionTier.Enable", false))
        {
          CloseGossipMenuFor(player);
          return false;
        }

        // Do not truncate an arbitrary network action to uint8: 356 would
        // otherwise alias tier 0 and 357 could alias a legitimate tier 1.
        if (action < 101 || action > 118)
        {
          CloseGossipMenuFor(player);
          return false;
        }
        uint8 tierToPurchase = static_cast<uint8>(action - 100);

        // Validate the purchase before taking any money so a failed service never costs gold
        if (!CanPurchaseProgressionTier(player, tierToPurchase))
        {
          CloseGossipMenuFor(player);
          return false;
        }

        uint32 cost = 0;
        if (!TryGetProgressionTierCost(tierToPurchase, cost))
        {
          ChatHandler(player->GetSession()).PSendSysMessage("The configured price for this progression tier is invalid.");
          CloseGossipMenuFor(player);
          return false;
        }
        if (!player->HasEnoughMoney(cost))
        {
          ChatHandler(player->GetSession()).PSendSysMessage("You do not have enough money for this service.");
          CloseGossipMenuFor(player);
          return false;
        }

        player->ModifyMoney(-static_cast<int32>(cost));
        bool const granted = ApplyProgressionTierPurchase(player, tierToPurchase);
        if (!granted)
        {
          // A missing/failed target stage must not leave the player poorer.
          // Source-only safety: full persistence/rollback still needs staging.
          player->ModifyMoney(static_cast<int32>(cost));
          ChatHandler(player->GetSession()).PSendSysMessage(
              "This progression tier could not be granted. Your gold has been refunded.");
        }
        CloseGossipMenuFor(player);
        return granted;
      }

      // Handle standard services (action IDs 1-4). Re-check the service is enabled
      // (and the action is valid) so a crafted gossip select cannot bypass the menu.
      if (!IsStandardServiceEnabled(action))
      {
        CloseGossipMenuFor(player);
        return false;
      }

      uint32 cost = GetServiceCost(player, action);
      if (!player->HasEnoughMoney(cost))
      {
        ChatHandler(player->GetSession()).PSendSysMessage("You do not have enough money for this service.");
        CloseGossipMenuFor(player);
        return false;
      }

      player->ModifyMoney(-cost);

      switch (action)
      {
          case 1:
            player->SetAtLoginFlag(AT_LOGIN_RENAME);
            ChatHandler(player->GetSession()).PSendSysMessage("{} flagged for name change at the character screen. Please log out.", player->GetPlayerName());
            break;
          case 2:
            player->SetAtLoginFlag(AT_LOGIN_CUSTOMIZE);
            ChatHandler(player->GetSession()).PSendSysMessage("{} flagged for appearance change at the character screen. Please log out.", player->GetPlayerName());
            break;
          case 3:
            player->SetAtLoginFlag(AT_LOGIN_CHANGE_RACE);
            ChatHandler(player->GetSession()).PSendSysMessage("{} flagged for race change at the character screen. Please log out.", player->GetPlayerName());
            break;
          case 4:
            player->SetAtLoginFlag(AT_LOGIN_CHANGE_FACTION);
            ChatHandler(player->GetSession()).PSendSysMessage("{} flagged for faction change at the character screen. Please log out.", player->GetPlayerName());
            break;
      }
      CloseGossipMenuFor(player);

      return true;
    }

    // Returns whether a standard service action (1-4) is enabled in the config.
    // Also acts as the valid-action guard: anything outside 1-4 returns false.
    bool IsStandardServiceEnabled(uint32 service)
    {
      switch (service)
      {
        case 1:
          return sConfigMgr->GetOption<bool>("CharacterServices.NameChange.Enable", false);
        case 2:
          return sConfigMgr->GetOption<bool>("CharacterServices.AppearanceChange.Enable", false);
        case 3:
          return sConfigMgr->GetOption<bool>("CharacterServices.RaceChange.Enable", false);
        case 4:
          return sConfigMgr->GetOption<bool>("CharacterServices.FactionChange.Enable", false);
        default:
          return false;
      }
    }

    // mod-individual-progression disables PROGRESSION_TBC_TIER_3 (value 11,
    // Zul'Aman), so the valid tier after PROGRESSION_TBC_TIER_2 (10) is
    // PROGRESSION_TBC_TIER_4 (12). Centralised here so the menu offer and the
    // purchase validation always agree on the single skipped tier.
    uint8 GetNextProgressionTier(uint8 currentTier)
    {
      if (currentTier == PROGRESSION_TBC_TIER_2)
        return PROGRESSION_TBC_TIER_4;
      return currentTier + 1;
    }

    // Validates a progression tier purchase without taking money or changing
    // state. Sends the player an explanatory message on each failure.
    bool CanPurchaseProgressionTier(Player* player, uint8 newTier)
    {
      if (!player || !player->GetSession())
          return false;

      uint8 currentTier = sIndividualProgression->GetPlayerProgressionFromQuests(player);
      uint8 maxAllowedTier = sConfigMgr->GetOption<uint8>("CharacterServices.ProgressionTier.MaxApplicableTier", 0);
      bool requireAccountUnlock = sConfigMgr->GetOption<bool>("CharacterServices.ProgressionTier.RequireAccountUnlock", true);

      // When RequireAccountUnlock is true (default), cap purchases at the account's
      // highest achieved tier. When false, the only ceiling is MaxApplicableTier (below).
      uint8 accountMaxTier = requireAccountUnlock
        ? sIndividualProgression->GetAccountProgression(player->GetSession()->GetAccountId())
        : PROGRESSION_WOTLK_TIER_5;

      // Cap the account's max tier by the configured maximum, if any
      if (maxAllowedTier > 0)
      {
        if (accountMaxTier > maxAllowedTier)
          accountMaxTier = maxAllowedTier;

        if (newTier > maxAllowedTier)
        {
          ChatHandler(player->GetSession()).PSendSysMessage("This progression tier is not available for purchase.");
          return false;
        }
      }

      // A higher-level account or forged generic gossip action must never
      // grant another era's entry OR final boss milestone on the paid path.
      if (!CanOfferProgressionTier(player, newTier))
      {
        ChatHandler(player->GetSession()).PSendSysMessage(
            "You must finish the current era and purchase the next expansion from Chronomancer Vezrath.");
        return false;
      }

      // Do not debit for a hidden quest marker that cannot be awarded.
      // ForceUpdateProgressionState silently skipped missing templates; the
      // new non-destructive grant and this target preflight avoid that path.
      if (sIndividualProgression->progressionLimit &&
          newTier > sIndividualProgression->progressionLimit)
      {
        ChatHandler(player->GetSession()).PSendSysMessage("This tier is above the server progression limit.");
        return false;
      }
      // UpdateProgressionState walks every intermediate reward marker.
      // Preflight those templates before taking gold, otherwise a 10 -> 12
      // advancement could partially grant tier 11 and then fail on tier 12.
      // Tier 11 is intentionally disabled in this IP fork.
      for (uint8 stage = currentTier + 1; stage <= newTier; ++stage)
      {
        if (stage == 11)
          continue;

        if (player->GetQuestStatus(66000u + stage) != QUEST_STATUS_REWARDED &&
            !sObjectMgr->GetQuestTemplate(66000u + stage))
        {
          ChatHandler(player->GetSession()).PSendSysMessage(
              "A required progression marker is unavailable. No gold was charged.");
          return false;
        }
      }

      // Only the immediate next tier may be purchased. This single check also
      // rejects already-owned tiers and any attempt to skip ahead, and it
      // correctly allows the 10 -> 12 step over the disabled tier 11.
      if (newTier != GetNextProgressionTier(currentTier))
      {
        ChatHandler(player->GetSession()).PSendSysMessage("You can only purchase the next progression tier.");
        return false;
      }

      // Cannot progress beyond what the account has unlocked elsewhere
      if (newTier > accountMaxTier)
      {
        ChatHandler(player->GetSession()).PSendSysMessage("You cannot progress beyond your account's maximum tier.");
        return false;
      }

      return true;
    }

    // Non-destructive incremental tier grant. Never clear old boss markers.
    // Return an actual post-condition instead of charging on a void call.
    bool ApplyProgressionTierPurchase(Player* player, uint8 newTier)
    {
      sIndividualProgression->UpdateProgressionState(player, static_cast<ProgressionState>(newTier));
      if (sIndividualProgression->GetPlayerProgressionFromQuests(player) < newTier ||
          player->GetQuestStatus(66000u + newTier) != QUEST_STATUS_REWARDED)
        return false;

      sIndividualProgression->checkIPPhasing(player, player->GetAreaId());
      ChatHandler(player->GetSession()).PSendSysMessage("You have successfully progressed to {}.", GetProgressionTierName(newTier));
      return true;
    }

    std::string GetTierIcon(uint8 tier)
    {
      switch (tier)
      {
        case PROGRESSION_START:
          return "Interface/Icons/inv_misc_map02";
        case PROGRESSION_MOLTEN_CORE:
          return "Interface/Icons/achievement_boss_ragnaros";
        case PROGRESSION_ONYXIA:
          return "Interface/Icons/achievement_boss_onyxia";
        case PROGRESSION_BLACKWING_LAIR:
          return "Interface/Icons/achievement_boss_nefarion";
        case PROGRESSION_PRE_AQ:
          return "Interface/Icons/inv_misc_qirajicrystal_05";
        case PROGRESSION_AQ_WAR:
          return "Interface/Icons/inv_misc_qirajicrystal_01";
        case PROGRESSION_AQ:
          return "Interface/Icons/achievement_boss_cthun";
        case PROGRESSION_NAXX40:
          return "Interface/Icons/achievement_boss_kelthuzad_01";
        case PROGRESSION_PRE_TBC:
          return "Interface/Icons/achievement_dungeon_karazhan";
        case PROGRESSION_TBC_TIER_1:
          return "Interface/Icons/achievement_boss_princemalchezaar_02";
        case PROGRESSION_TBC_TIER_2:
          return "Interface/Icons/achievement_boss_kael'thassunstrider_01";
        case PROGRESSION_TBC_TIER_4:
          return "Interface/Icons/achievement_boss_illidan";
        case PROGRESSION_TBC_TIER_5:
          return "Interface/Icons/achievement_boss_kiljaeden";
        case PROGRESSION_WOTLK_TIER_1:
          return "Interface/Icons/achievement_boss_kelthuzad_01";
        case PROGRESSION_WOTLK_TIER_2:
          return "Interface/Icons/achievement_boss_yoggsaron_01";
        case PROGRESSION_WOTLK_TIER_3:
          return "Interface/Icons/achievement_boss_anubarak_01";
        case PROGRESSION_WOTLK_TIER_4:
          return "Interface/Icons/achievement_boss_lichking";
        case PROGRESSION_WOTLK_TIER_5:
          return "Interface/Icons/achievement_boss_halion";
        default:
          return "Interface/Icons/inv_misc_questionmark";
      }
    }

    std::string GetProgressionTierName(uint8 tier)
    {
      switch (tier)
      {
        case PROGRESSION_START:
          return "Start";
        case PROGRESSION_MOLTEN_CORE:
          return "Molten Core";
        case PROGRESSION_ONYXIA:
          return "Onyxia's Lair";
        case PROGRESSION_BLACKWING_LAIR:
          return "Blackwing Lair";
        case PROGRESSION_PRE_AQ:
          return "Pre-AQ";
        case PROGRESSION_AQ_WAR:
          return "AQ War Effort";
        case PROGRESSION_AQ:
          return "Ahn'Qiraj";
        case PROGRESSION_NAXX40:
          return "Naxxramas (Vanilla)";
        case PROGRESSION_PRE_TBC:
          return "Pre-TBC";
        case PROGRESSION_TBC_TIER_1:
          return "TBC Tier 1";
        case PROGRESSION_TBC_TIER_2:
          return "TBC Tier 2";
        case PROGRESSION_TBC_TIER_4:
          return "TBC Tier 4";
        case PROGRESSION_TBC_TIER_5:
          return "TBC Tier 5";
        case PROGRESSION_WOTLK_TIER_1:
          return "WotLK Tier 1";
        case PROGRESSION_WOTLK_TIER_2:
          return "WotLK Tier 2";
        case PROGRESSION_WOTLK_TIER_3:
          return "WotLK Tier 3";
        case PROGRESSION_WOTLK_TIER_4:
          return "WotLK Tier 4";
        case PROGRESSION_WOTLK_TIER_5:
          return "WotLK Tier 5";
        default:
          return "Unknown Tier";
      }
    }

    // Progression tiers use a static, configurable per-tier cost. DynamicCost
    // scaling intentionally does not apply here (it only affects the standard
    // name/appearance/race/faction services via GetServiceCost).
    // For generic tier purchases, retain a valid zero-price owner setting,
    // but reject signed-money overflow rather than wrapping to a cheap price.
    bool TryGetProgressionTierCost(uint8 tier, uint32& copper)
    {
      std::string const configOption = "CharacterServices.Cost.ProgressionTier." + std::to_string(tier);
      uint32 const defaultGold = 100u + (static_cast<uint32>(tier) * 50u);
      uint32 const gold = sConfigMgr->GetOption<uint32>(configOption, defaultGold);
      return CharacterServicesMoneyPolicy::TryGoldToCopper(gold, true, copper);
    }

    uint32 GetServiceCost(Player* player, uint8 service)
    {
       bool dynamicCostEnabled = sConfigMgr->GetOption<bool>("CharacterServices.DynamicCost.Enable", false);
       double playerLevel = player->GetLevel();
       double dynamicRatio = (playerLevel / 80);
       switch (service)
       {
         case 1:
           {
             uint32 serviceCost = sConfigMgr->GetOption<uint32>("CharacterServices.Cost.NameChange", 25) * 10000;
             return dynamicCostEnabled ? dynamicRatio * serviceCost : serviceCost;
           }
         case 2:
           {
             uint32 serviceCost = sConfigMgr->GetOption<uint32>("CharacterServices.Cost.AppearanceChange", 50) * 10000;
             return dynamicCostEnabled ? dynamicRatio * serviceCost : serviceCost;
           }
         case 3:
           {
             uint32 serviceCost = sConfigMgr->GetOption<uint32>("CharacterServices.Cost.RaceChange", 100) * 10000;
             return dynamicCostEnabled ? dynamicRatio * serviceCost : serviceCost;
           }
         case 4:
           {
             uint32 serviceCost = sConfigMgr->GetOption<uint32>("CharacterServices.Cost.FactionChange", 250) * 10000;
             return dynamicCostEnabled ? dynamicRatio * serviceCost : serviceCost;
           }
         default:
           return 250 * 10000;
       }
    }
};

void AddCharacterServicesScripts()
{
    new CharacterServices();
};
