"use client";

import { useState, useEffect } from "react";

interface ItemInfo {
    id: number;
    name: string;
    dname: string;
    cost: number;
    img: string;
}

type ItemMap = Record<number, ItemInfo>;

let cachedItemMap: ItemMap | null = null;

export function useItemMap() {
    const [itemMap, setItemMap] = useState<ItemMap>(cachedItemMap || {});

    useEffect(() => {
        if (cachedItemMap) return;
        fetch("https://api.opendota.com/api/constants/items")
            .then((res) => res.json())
            .then((raw: Record<string, { id?: number; dname?: string; cost?: number; img?: string }>) => {
                const map: ItemMap = {};
                for (const [key, data] of Object.entries(raw)) {
                    if (data.id != null) {
                        map[data.id] = {
                            id: data.id,
                            name: key,
                            dname: data.dname || "?",
                            cost: data.cost || 0,
                            img: data.img ? `https://cdn.cloudflare.steamstatic.com${data.img}` : "",
                        };
                    }
                }
                cachedItemMap = map;
                setItemMap(map);
            })
            .catch(() => { });
    }, []);

    return itemMap;
}

export function resolveSlots(
    itemsFinal: Record<string, number> | null,
    itemMap: ItemMap
): ItemInfo[] {
    if (!itemsFinal) return [];
    const items: ItemInfo[] = [];
    for (let i = 0; i < 6; i++) {
        const id = itemsFinal[`slot_${i}`];
        if (id && itemMap[id]) {
            items.push(itemMap[id]);
        }
    }
    return items;
}

export function getItemTiming(itemKey: string, purchaseLog: { time: number; key: string }[] | null): string | null {
    if (!purchaseLog || !itemKey) return null;

    // Some items have prefixes/suffixes in their key compared to the ID name
    const normalizedItemKey = itemKey.replace('recipe_', '');

    // Find the purchase event. Try exact match first, then flexible match.
    // Also we want the LATEST purchase time for the item (in case it was bought, sold, bought again)
    let purchase = purchaseLog.slice().reverse().find(p => p.key === itemKey);
    if (!purchase) {
        purchase = purchaseLog.slice().reverse().find(p =>
            p.key.includes(normalizedItemKey) || normalizedItemKey.includes(p.key)
        );
    }
    if (!purchase) return null;

    let time = purchase.time;
    if (time < 0) {
        time = -time;
        const mins = Math.floor(time / 60).toString().padStart(2, "0");
        const secs = (time % 60).toString().padStart(2, "0");
        return `-${mins}:${secs}`;
    } else {
        const mins = Math.floor(time / 60).toString().padStart(2, "0");
        const secs = (time % 60).toString().padStart(2, "0");
        return `${mins}:${secs}`;
    }
}
