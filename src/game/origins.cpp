#include "game/origins.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <string>

namespace opense4::game::origins {

namespace {

constexpr OriginModifier mod(Characteristic characteristic, int amount) { return {characteristic, amount}; }

constexpr std::array<StartingOriginInfo, 20> kOrigins{{
    {StartingOrigin::FirstWaveDiaspora, "First-Wave Diaspora",
     "Your people were scattered across the frontier in a desperate first exodus. New settlements grow quickly and local councils cooperate, but the young colonies have little appetite for war.",
     {mod(Characteristic::Reproduction, 10), mod(Characteristic::PoliticalSavvy, 8), mod(Characteristic::Aggressiveness, -8)},
     Resources{0, 2500, 0}, 0, 1, 0, 0},
    {StartingOrigin::IndustrialDirectorate, "Industrial Directorate",
     "A central production authority coordinated mines, foundries and orbital construction long before unification. Heavy industry starts ahead of schedule, at the expense of public contentment.",
     {mod(Characteristic::MiningAptitude, 12), mod(Characteristic::ConstructionAptitude, 8), mod(Characteristic::Happiness, -8)},
     Resources{5000, 0, 0}, 0, 0, 0, 0},
    {StartingOrigin::ScientificEnclave, "Scientific Enclave",
     "Your civilization grew around universities and experimental habitats. Brilliant researchers and intelligence networks drive discovery, while a narrow academic elite neglects physical training.",
     {mod(Characteristic::Intelligence, 12), mod(Characteristic::Cunning, 8), mod(Characteristic::PhysicalStrength, -8)},
     Resources{0, 0, 3000}, 0, 0, 0, 0},
    {StartingOrigin::NavalHeritage, "Naval Heritage",
     "Centuries of escort duty and convoy warfare forged a culture that trusts its admirals. Crews are aggressive and disciplined in battle, but civilian extraction industries remain underdeveloped.",
     {mod(Characteristic::Aggressiveness, 10), mod(Characteristic::Defensiveness, 8), mod(Characteristic::MiningAptitude, -8)},
     Resources{2500, 0, 0}, 0, 0, 0, 0},
    {StartingOrigin::CitadelWorld, "Citadel World",
     "Your homeworld survived repeated sieges behind layered planetary defences. Citizens and soldiers excel at holding ground, but generations spent inside fortified cities slowed population growth.",
     {mod(Characteristic::Defensiveness, 12), mod(Characteristic::PhysicalStrength, 8), mod(Characteristic::Reproduction, -10)},
     Resources{3000, 0, 0}, 0, 0, 0, 0},
    {StartingOrigin::MerchantConsortium, "Merchant Consortium",
     "Independent trading houses pooled their fleets and capital to form a single polity. Negotiators secure favourable exchanges and contented crews, while the boardrooms avoid costly offensives.",
     {mod(Characteristic::PoliticalSavvy, 12), mod(Characteristic::Happiness, 8), mod(Characteristic::Aggressiveness, -8)},
     Resources{0, 4000, 0}, 0, 0, 0, 0},
    {StartingOrigin::AgrarianHearth, "Agrarian Hearth",
     "Your first cities were built around vast climate-controlled food belts and communal granaries. Farms and family settlements flourish, but less attention was given to mineral extraction.",
     {mod(Characteristic::FarmingAptitude, 12), mod(Characteristic::Reproduction, 8), mod(Characteristic::MiningAptitude, -8)},
     Resources{0, 5000, 0}, 0, 0, 0, 0},
    {StartingOrigin::DeepCrustProspectors, "Deep-Crust Prospectors",
     "The first great fortunes came from hazardous mantle drills and buried radioactive seams. Prospectors are unmatched at finding raw materials, but politics has always taken a back seat to the next strike.",
     {mod(Characteristic::MiningAptitude, 14), mod(Characteristic::RefiningAptitude, 8), mod(Characteristic::PoliticalSavvy, -8)},
     Resources{5000, 0, 0}, 0, 0, 0, 0},
    {StartingOrigin::ReactorGuild, "Reactor Guild",
     "Power cooperatives became the most trusted institutions on your homeworld. Their reactor expertise supports research and fuel production, though food production never received the same investment.",
     {mod(Characteristic::RefiningAptitude, 14), mod(Characteristic::Intelligence, 8), mod(Characteristic::FarmingAptitude, -8)},
     Resources{0, 0, 5000}, 0, 0, 0, 0},
    {StartingOrigin::LogisticsCombine, "Logistics Combine",
     "Your earliest intercontinental alliance was built by freight operators, depot keepers and repair yards. Supply chains are lean and equipment is maintained efficiently; the culture is cautious about direct conflict.",
     {mod(Characteristic::MaintenanceAptitude, 12), mod(Characteristic::RepairAptitude, 8), mod(Characteristic::Aggressiveness, -8)},
     Resources{2000, 2000, 2000}, 0, 0, 0, 1},
    {StartingOrigin::PathfinderInitiative, "Pathfinder Initiative",
     "Long-range survey crews and route cartographers shaped national policy. Your scouts are resourceful and crews adapt to harsh environments, but the fleet doctrine favours discovery over static defence.",
     {mod(Characteristic::Cunning, 12), mod(Characteristic::EnvironmentalResistance, 8), mod(Characteristic::Defensiveness, -8)},
     Resources{0, 0, 3000}, 0, 0, 0, 0},
    {StartingOrigin::TerraformingMandate, "Terraforming Mandate",
     "A planetary engineering compact united the first settlements around a shared promise: make hostile worlds habitable. Population systems and environmental adaptation are advanced, but military priorities were postponed.",
     {mod(Characteristic::EnvironmentalResistance, 12), mod(Characteristic::Reproduction, 8), mod(Characteristic::Aggressiveness, -8)},
     Resources{0, 3000, 0}, 0, 0, 0, 0},
    {StartingOrigin::CyberneticCollective, "Cybernetic Collective",
     "Industrial implants and machine-assisted planning are woven into everyday life. Precision engineering and applied science are strong, but low birth rates make population growth a persistent concern.",
     {mod(Characteristic::Intelligence, 12), mod(Characteristic::ConstructionAptitude, 8), mod(Characteristic::Reproduction, -10)},
     Resources{2500, 0, 2500}, 0, 0, 0, 0},
    {StartingOrigin::PsionicCovenant, "Psionic Covenant",
     "A shared tradition of meditation and collective consciousness formed a resilient social order. Citizens remain content and intelligence services are perceptive, while physical conditioning is less culturally valued.",
     {mod(Characteristic::Happiness, 12), mod(Characteristic::Cunning, 8), mod(Characteristic::PhysicalStrength, -8)},
     Resources{0, 3000, 0}, 0, 0, 0, 0},
    {StartingOrigin::DiplomaticAssembly, "Diplomatic Assembly",
     "Your empire was founded by a congress of rival worlds that chose treaties over conquest. Social cohesion and public education are exceptional, but the armed forces lack an offensive tradition.",
     {mod(Characteristic::Happiness, 12), mod(Characteristic::Intelligence, 8), mod(Characteristic::Aggressiveness, -10)},
     Resources{2000, 2000, 0}, 1500, 0, 0, 0},
    {StartingOrigin::WarbornClans, "Warborn Clans",
     "Clan fleets once fought over every orbit and asteroid field before one warlord united them. Tough crews and an aggressive command culture remain, but agriculture was neglected during the wars of unification.",
     {mod(Characteristic::PhysicalStrength, 12), mod(Characteristic::Aggressiveness, 10), mod(Characteristic::FarmingAptitude, -12)},
     Resources{4000, 0, 0}, 0, 0, 0, 0},
    {StartingOrigin::EcologicalStewardship, "Ecological Stewardship",
     "Your ancestors learned to live within strict planetary limits and restore ecosystems before expanding. Adaptive populations and sustainable farms thrive, while aggressive extraction is politically restricted.",
     {mod(Characteristic::EnvironmentalResistance, 12), mod(Characteristic::FarmingAptitude, 8), mod(Characteristic::MiningAptitude, -10)},
     Resources{0, 4000, 0}, 0, 0, 0, 0},
    {StartingOrigin::SalvageGuild, "Salvage Guild",
     "A belt-wide network of reclaimers turned wreckage into the foundations of a modern economy. Repair crews and maintenance planners excel, though research institutions receive less public investment.",
     {mod(Characteristic::RepairAptitude, 12), mod(Characteristic::MaintenanceAptitude, 8), mod(Characteristic::Intelligence, -8)},
     Resources{3000, 0, 2000}, 0, 0, 0, 0},
    {StartingOrigin::AncientTechnocracy, "Ancient Technocracy",
     "Your capital was built atop the surviving infrastructure of a vanished precursor age. The state inherited formidable technical institutions and an early research archive, but its ageing population is slow to expand.",
     {mod(Characteristic::Intelligence, 10), mod(Characteristic::ConstructionAptitude, 10), mod(Characteristic::Reproduction, -10)},
     Resources{0, 0, 3000}, 3000, 0, 0, 0},
    {StartingOrigin::VoidbornNomads, "Voidborn Nomads",
     "Your people lived for generations aboard mobile habitats and convoy fleets before claiming a permanent world. Crews are adaptable and defensive in space, but planetary diplomacy is a young discipline.",
     {mod(Characteristic::Cunning, 12), mod(Characteristic::Defensiveness, 8), mod(Characteristic::PoliticalSavvy, -10)},
     Resources{0, 0, 2500}, 0, 0, 1, 0},
}};

constexpr StartingOriginInfo kNone{
    StartingOrigin::None, "No Origin",
    "A standard beginning with no inherited advantages or disadvantages. Your empire starts on equal terms and defines its identity through play.",
    {}, Resources{}, 0, 0, 0, 0};

std::string normalise(std::string_view value) {
    std::string out;
    out.reserve(value.size());
    for (unsigned char c : value)
        if (std::isalnum(c)) out.push_back(static_cast<char>(std::tolower(c)));
    return out;
}

} // namespace

std::span<const StartingOriginInfo> all() { return kOrigins; }

const StartingOriginInfo& info(StartingOrigin origin) {
    if (origin == StartingOrigin::None) return kNone;
    const size_t index = static_cast<size_t>(origin) - 1;
    return index < kOrigins.size() ? kOrigins[index] : kNone;
}

std::optional<StartingOrigin> fromName(std::string_view name) {
    const std::string wanted = normalise(name);
    if (wanted.empty()) return std::nullopt;
    if (wanted == normalise(kNone.name)) return StartingOrigin::None;
    for (const StartingOriginInfo& origin : kOrigins)
        if (normalise(origin.name) == wanted) return origin.id;
    return std::nullopt;
}

void applyToRace(Race& race, StartingOrigin origin) {
    for (const OriginModifier& modifier : info(origin).modifiers) {
        const size_t index = static_cast<size_t>(modifier.characteristic);
        if (index < race.characteristics.size()) race.characteristics[index] += modifier.amount;
    }
}

void removeFromRace(Race& race, StartingOrigin origin) {
    for (const OriginModifier& modifier : info(origin).modifiers) {
        const size_t index = static_cast<size_t>(modifier.characteristic);
        if (index < race.characteristics.size()) race.characteristics[index] -= modifier.amount;
    }
}

} // namespace opense4::game::origins
