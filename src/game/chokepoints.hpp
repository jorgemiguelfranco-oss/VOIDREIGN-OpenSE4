#pragma once

// Strategic choke points are articulation vertices in the warp network the
// player has actually explored. Unknown systems and links are excluded, so
// this view never reveals hidden galaxy topology.
#include "game/state.hpp"

#include <algorithm>
#include <cstdint>
#include <functional>
#include <vector>

namespace opense4::game {

inline std::vector<SystemId> exploredChokepoints(const Galaxy& galaxy, const Empire& viewer) {
    const size_t count = galaxy.systems.size();
    std::vector<uint8_t> known(count, 0);
    for (const StarSystem& sys : galaxy.systems)
        if (sys.id.index() < count && viewer.hasExplored(sys.id)) known[sys.id.index()] = 1;

    std::vector<std::vector<size_t>> adjacent(count);
    auto connect = [&](size_t a, size_t b) {
        if (a == b || a >= count || b >= count || !known[a] || !known[b]) return;
        auto add = [](std::vector<size_t>& list, size_t value) {
            if (std::find(list.begin(), list.end(), value) == list.end()) list.push_back(value);
        };
        add(adjacent[a], b);
        add(adjacent[b], a);
    };

    for (const StarSystem& sys : galaxy.systems) {
        const size_t from = sys.id.index();
        if (from >= count || !known[from]) continue;
        for (ObjectId id : sys.objects) {
            if (!id.valid() || id.index() >= galaxy.objects.size()) continue;
            const SpaceObject& warp = galaxy.object(id);
            if (warp.kind != ObjectKind::WarpPoint || !warp.destination.valid() ||
                warp.destination.index() >= galaxy.objects.size()) continue;
            const SpaceObject& paired = galaxy.object(warp.destination);
            if (paired.kind != ObjectKind::WarpPoint) continue;
            connect(from, paired.system.index());
        }
    }

    std::vector<int> discovered(count, -1), low(count, -1), parent(count, -1);
    std::vector<uint8_t> articulation(count, 0);
    int clock = 0;
    std::function<void(size_t)> visit = [&](size_t at) {
        discovered[at] = low[at] = clock++;
        int children = 0;
        for (size_t next : adjacent[at]) {
            if (discovered[next] < 0) {
                parent[next] = static_cast<int>(at);
                ++children;
                visit(next);
                low[at] = std::min(low[at], low[next]);
                if (parent[at] < 0 && children > 1) articulation[at] = 1;
                if (parent[at] >= 0 && low[next] >= discovered[at]) articulation[at] = 1;
            } else if (static_cast<int>(next) != parent[at]) {
                low[at] = std::min(low[at], discovered[next]);
            }
        }
    };

    for (size_t i = 0; i < count; ++i)
        if (known[i] && discovered[i] < 0) visit(i);

    std::vector<SystemId> result;
    for (size_t i = 0; i < count; ++i)
        if (articulation[i]) result.push_back(SystemId{static_cast<uint32_t>(i)});
    return result; // already sorted by SystemId
}

} // namespace opense4::game
