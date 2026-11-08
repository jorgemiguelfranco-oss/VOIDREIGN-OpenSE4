#include "client/classic/screens/screens.hpp"

#include "game/commands.hpp"
#include "game/leaders.hpp"

#include <algorithm>
#include <format>
#include <string>
#include <utility>

namespace opense4::client::classic {

namespace {

using game::Leader;
using game::LeaderRole;
using game::LeaderRarity;
using game::EmpireId;

std::string assignmentName(const game::GameState& state, const Leader& leader) {
    if (leader.role == LeaderRole::Ruler) return "Head of state";
    if (leader.assignedColony.valid()) {
        const game::SpaceObject& planet = state.galaxy.object(leader.assignedColony);
        return std::format("{} at {}", leader.role == LeaderRole::General ? "General" : "Governor", planet.name);
    }
    if (leader.assignedFleet.valid()) {
        const game::Fleet* fleet = state.fleet(leader.assignedFleet);
        if (fleet) return std::format("{} of {}", leader.role == LeaderRole::General ? "General" : "Admiral", fleet->name);
    }
    if (leader.role == LeaderRole::Scientist) return "Empire research staff";
    return "Unassigned";
}

uint32_t nextXp(const Leader& leader) {
    return game::leaders::experienceForNextLevel(leader.level);
}

} // namespace

class LeaderRosterScreen final : public Screen {
public:
    bool draw(UiContext& ui) override {
        Dialog d(ui, "VOIDREIGN Leadership Corps", DialogSize::Large);
        if (!d.open()) return d.keepOpen();

        d.beginContent();
        const game::Empire& empire = ui.me();
        const game::GameState& state = ui.state();
        const size_t active = static_cast<size_t>(std::count_if(empire.leaders.begin(), empire.leaders.end(),
            [](const Leader& leader) { return leader.alive; }));
        const game::Resources upkeep = game::leaders::upkeep(empire);
        ImGui::TextColored(kLabelBlue, "COMMAND STAFF  %zu / %zu", active, game::leaders::kMaximumActiveLeaders);
        ImGui::SameLine();
        ImGui::TextDisabled("   Recurring upkeep:");
        ImGui::SameLine();
        resources(ui, upkeep, true);
        ImGui::Separator();
        ImGui::TextWrapped("Officers gain experience through service, improve their abilities as they level, and can die of old age. Rare Paragons start with exceptional training and live longer.");
        ImGui::Spacing();

        if (ImGui::BeginChild("leaders:roster", ImVec2(0, ui.px(355)), true)) {
            bool found = false;
            for (const Leader& leader : empire.leaders) {
                if (!leader.alive) continue;
                found = true;
                ImGui::PushID(static_cast<int>(leader.id));
                ImGui::BeginGroup();
                image(ui, ui.art.racePortrait(empire.race.style), {64, 64});
                ImGui::SameLine();
                ImGui::BeginGroup();
                ImGui::TextColored(kLabelBlue, "%s", leader.name.c_str());
                ImGui::TextDisabled("%s — %s", std::string(game::leaders::displayName(leader.role)).c_str(),
                                    leader.epithet.c_str());
                const ImVec4 rarityColor = leader.rarity == LeaderRarity::Paragon
                    ? ImVec4(1.0f, 0.80f, 0.35f, 1.0f)
                    : leader.rarity == LeaderRarity::Veteran
                        ? ImVec4(0.60f, 0.82f, 1.0f, 1.0f)
                        : ImVec4(0.75f, 0.78f, 0.83f, 1.0f);
                ImGui::TextColored(rarityColor, "%s", std::string(game::leaders::displayName(leader.rarity)).c_str());
                ImGui::SameLine();
                ImGui::Text("  Level %u  |  Age %u", unsigned(leader.level), unsigned(leader.age));
                ImGui::EndGroup();
                ImGui::EndGroup();
                const uint32_t required = std::max<uint32_t>(1, nextXp(leader));
                const float xp = std::clamp(float(leader.experience) / float(required), 0.0f, 1.0f);
                ImGui::ProgressBar(xp, ImVec2(-1.0f, ui.px(12)), std::format("{} / {} XP", leader.experience, required).c_str());
                if (leader.secondaryTrait != game::LeaderTrait::Count) {
                    ImGui::TextWrapped("%s — %s: %s",
                        std::string(game::leaders::displayName(leader.trait)).c_str(),
                        std::string(game::leaders::displayName(leader.secondaryTrait)).c_str(),
                        std::string(game::leaders::description(leader.secondaryTrait)).c_str());
                } else {
                    ImGui::TextWrapped("%s — %s", std::string(game::leaders::displayName(leader.trait)).c_str(),
                                       std::string(game::leaders::description(leader.trait)).c_str());
                }
                ImGui::TextDisabled("%s", assignmentName(state, leader).c_str());

                if (leader.role == LeaderRole::Governor || leader.role == LeaderRole::General) {
                    const std::string preview = leader.assignedColony.valid()
                        ? state.galaxy.object(leader.assignedColony).name : "Unassigned";
                    if (ImGui::BeginCombo("Colony assignment", preview.c_str())) {
                        if (ImGui::Selectable("Unassign", !leader.assignedColony.valid() && !leader.assignedFleet.valid()))
                            issue(ui, game::cmd::AssignLeader{leader.id, {}, {}});
                        for (const auto& colony : state.colonies) {
                            if (!colony || colony->owner != ui.session.player()) continue;
                            const std::string name = state.galaxy.object(colony->planet).name;
                            const bool selected = leader.assignedColony == colony->planet;
                            if (ImGui::Selectable(name.c_str(), selected))
                                issue(ui, game::cmd::AssignLeader{leader.id, colony->planet, {}});
                        }
                        ImGui::EndCombo();
                    }
                    ui.tagItem("leaders:assign-colony");
                }
                if (leader.role == LeaderRole::Admiral || leader.role == LeaderRole::General) {
                    const game::Fleet* assigned = state.fleet(leader.assignedFleet);
                    const std::string preview = assigned ? assigned->name : "Unassigned";
                    if (ImGui::BeginCombo("Fleet assignment", preview.c_str())) {
                        if (ImGui::Selectable("Unassign fleet", !leader.assignedFleet.valid()))
                            issue(ui, game::cmd::AssignLeader{leader.id, {}, {}});
                        for (const game::Fleet& fleet : state.fleets) {
                            if (fleet.owner != ui.session.player()) continue;
                            const bool selected = leader.assignedFleet == fleet.id;
                            if (ImGui::Selectable(fleet.name.c_str(), selected))
                                issue(ui, game::cmd::AssignLeader{leader.id, {}, fleet.id});
                        }
                        ImGui::EndCombo();
                    }
                    ui.tagItem("leaders:assign-fleet");
                }
                if (leader.role == LeaderRole::Scientist)
                    ImGui::TextDisabled("Works empire-wide; research bonus is applied automatically.");
                if (leader.role == LeaderRole::Ruler) {
                    ImGui::TextDisabled("Sovereign of the empire; succession is automatic on natural death.");
                } else {
                    if (ImGui::SmallButton("Dismiss"))
                        issue(ui, game::cmd::DismissLeader{leader.id});
                    ui.tagItem("leaders:dismiss");
                }
                ImGui::Separator();
                ImGui::PopID();
            }
            if (!found) ImGui::TextDisabled("No active leaders. Recruit officers to rebuild your command staff.");
            ImGui::EndChild();
        }

        ImGui::Spacing();
        ImGui::TextColored(kLabelBlue, "RECRUIT OFFICERS");
        const game::Resources cost{game::leaders::kRecruitMinerals, game::leaders::kRecruitOrganics,
                                   game::leaders::kRecruitRadioactives};
        ImGui::TextDisabled("Cost per recruit:");
        ImGui::SameLine();
        resources(ui, cost, true);
        const bool canRecruit = active < game::leaders::kMaximumActiveLeaders && empire.stockpile.covers(cost);
        auto recruitButton = [&](const char* title, LeaderRole role) {
            ImGui::BeginDisabled(!canRecruit || (role == LeaderRole::Scientist &&
                std::any_of(empire.leaders.begin(), empire.leaders.end(), [](const Leader& l) {
                    return l.alive && l.role == LeaderRole::Scientist;
                })));
            if (ImGui::Button(title, ImVec2(ui.px(130), ui.px(26))))
                issue(ui, game::cmd::RecruitLeader{role});
            ImGui::EndDisabled();
            ui.tagItem(std::format("leaders:recruit-{}", std::string(game::leaders::displayName(role))).c_str());
        };
        recruitButton("Governor", LeaderRole::Governor);
        ImGui::SameLine();
        recruitButton("Admiral", LeaderRole::Admiral);
        ImGui::SameLine();
        recruitButton("Scientist", LeaderRole::Scientist);
        ImGui::SameLine();
        recruitButton("General", LeaderRole::General);

        if (!error_.empty()) ImGui::TextColored(ImVec4(1.0f, 0.42f, 0.34f, 1.0f), "%s", error_.c_str());

        bool history = false;
        for (const Leader& leader : empire.leaders) history = history || !leader.alive;
        if (history && ImGui::CollapsingHeader("Deceased and retired leaders")) {
            for (const Leader& leader : empire.leaders) {
                if (leader.alive) continue;
                ImGui::TextDisabled("%s — %s, Level %u, age %u — %s (turn %u)",
                    leader.name.c_str(), std::string(game::leaders::displayName(leader.role)).c_str(),
                    unsigned(leader.level), unsigned(leader.age), leader.deathCause.c_str(), leader.deathTurn);
            }
        }

        d.beginButtons();
        d.close();
        return d.keepOpen();
    }

private:
    void issue(UiContext& ui, game::Command command) {
        const game::CommandResult result = ui.session.issue(std::move(command));
        error_ = result.ok ? std::string{} : result.error;
    }

    std::string error_;
};

std::unique_ptr<Screen> makeLeaders(const ScreenArgs&) { return std::make_unique<LeaderRosterScreen>(); }

} // namespace opense4::client::classic
