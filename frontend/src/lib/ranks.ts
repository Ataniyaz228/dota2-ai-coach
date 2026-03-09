/**
 * Dota 2 Rank / MMR mapping utility.
 *
 * OpenDota returns `rank_tier` as a 2-digit number:
 *   tens digit = medal (1=Herald .. 8=Immortal)
 *   ones digit = star (0-5, 0 = no stars)
 *
 * This utility provides:
 * - Correct medal name from rank_tier
 * - Estimated MMR range from rank_tier
 * - Consistent display strings
 */

interface RankInfo {
    medal: string;
    stars: number;
    mmrLow: number;
    mmrHigh: number;
    display: string;
    mmrEstimate: number;
}

const MEDALS: Record<number, { name: string; baseMmr: number }> = {
    1: { name: "Herald", baseMmr: 0 },
    2: { name: "Guardian", baseMmr: 770 },
    3: { name: "Crusader", baseMmr: 1540 },
    4: { name: "Archon", baseMmr: 2310 },
    5: { name: "Legend", baseMmr: 3080 },
    6: { name: "Ancient", baseMmr: 3850 },
    7: { name: "Divine", baseMmr: 4620 },
    8: { name: "Immortal", baseMmr: 5420 },
};

const MMR_PER_STAR = 154;

export function parseRankTier(rankTier: number | null | undefined): RankInfo {
    if (!rankTier || rankTier < 10) {
        return {
            medal: "Uncalibrated",
            stars: 0,
            mmrLow: 0,
            mmrHigh: 0,
            display: "Uncalibrated",
            mmrEstimate: 0,
        };
    }

    const medalNum = Math.floor(rankTier / 10);
    const stars = rankTier % 10;

    const medalInfo = MEDALS[medalNum];
    if (!medalInfo) {
        return {
            medal: "Unknown",
            stars: 0,
            mmrLow: 0,
            mmrHigh: 0,
            display: "Unknown",
            mmrEstimate: 0,
        };
    }

    const mmrLow = medalInfo.baseMmr + stars * MMR_PER_STAR;
    const mmrHigh = mmrLow + MMR_PER_STAR - 1;
    const mmrEstimate = mmrLow + Math.floor(MMR_PER_STAR / 2);

    const starSuffix = stars > 0 ? ` ${stars}` : "";
    const display = `${medalInfo.name}${starSuffix}`;

    return { medal: medalInfo.name, stars, mmrLow, mmrHigh, display, mmrEstimate };
}

export function formatMmrRange(info: RankInfo): string {
    if (info.mmrEstimate === 0) return "—";
    return `~${info.mmrEstimate}`;
}
