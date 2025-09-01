import { createDebounce } from "./throttle.js";
const DEFAULT_STORAGE_KEY = "starhtml-persist";
const DEFAULT_THROTTLE = 500;
function getStorage(isSession) {
  try {
    const storage = isSession ? sessionStorage : localStorage;
    const testKey = "__test__";
    storage.setItem(testKey, "1");
    storage.removeItem(testKey);
    return storage;
  } catch {
    return null;
  }
}
function parseConfig(ctx) {
  const { key, value, mods } = ctx;
  const isSession = mods.has("session");
  const storage = getStorage(isSession);
  if (!storage) return null;
  const storageKey = key ? `${DEFAULT_STORAGE_KEY}-${key}` : DEFAULT_STORAGE_KEY;
  let signals = [];
  let isWildcard = false;
  const trimmedValue = value?.trim();
  if (trimmedValue) {
    signals = trimmedValue.split(",").map((s) => s.trim()).filter(Boolean);
  } else {
    isWildcard = true;
  }
  return { storage, storageKey, signals, isWildcard };
}
function loadFromStorage(config, ctx) {
  try {
    const stored = config.storage.getItem(config.storageKey);
    if (!stored) return;
    const data = JSON.parse(stored);
    if (!data || typeof data !== "object") return;
    ctx.startBatch();
    try {
      if (config.isWildcard) {
        ctx.mergePatch(data);
      } else {
        const patch = Object.fromEntries(
          config.signals.filter((signal) => signal in data).map((signal) => [signal, data[signal]])
        );
        if (Object.keys(patch).length > 0) {
          ctx.mergePatch(patch);
        }
      }
    } finally {
      ctx.endBatch();
    }
  } catch {
  }
}
function getSignalsFromElement(el) {
  const signals = [];
  for (const attr of el.attributes) {
    if (attr.name.startsWith("data-signals-")) {
      const signalName = attr.name.substring("data-signals-".length);
      if (signalName) {
        signals.push(signalName);
      }
    }
  }
  return signals;
}
function saveToStorage(config, _ctx, signalData) {
  try {
    const stored = config.storage.getItem(config.storageKey);
    const existing = stored ? JSON.parse(stored) : {};
    const merged = { ...existing, ...signalData };
    if (Object.keys(merged).length > 0) {
      config.storage.setItem(config.storageKey, JSON.stringify(merged));
    }
  } catch {
  }
}
const persistAttributePlugin = {
  type: "attribute",
  name: "persist",
  keyReq: "allowed",
  valReq: "allowed",
  shouldEvaluate: false,
  onLoad(ctx) {
    const config = parseConfig(ctx);
    if (!config) return;
    loadFromStorage(config, ctx);
    const throttleMs = ctx.mods.has("immediate") ? 0 : Number.parseInt(String(ctx.mods.get("throttle") ?? DEFAULT_THROTTLE));
    let cachedSignalData = {};
    const persistData = () => {
      if (Object.keys(cachedSignalData).length > 0) {
        saveToStorage(config, ctx, cachedSignalData);
      }
    };
    const throttledPersist = throttleMs > 0 ? createDebounce(persistData, throttleMs) : persistData;
    const cleanup = ctx.effect(() => {
      const signals = config.isWildcard ? getSignalsFromElement(ctx.el) : config.signals;
      const data = {};
      for (const signal of signals) {
        try {
          data[signal] = ctx.getPath(signal);
        } catch {
        }
      }
      cachedSignalData = data;
      throttledPersist();
    });
    return cleanup;
  }
};
var persist_default = persistAttributePlugin;
export {
  persist_default as default
};
