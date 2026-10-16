import { useCallback, useEffect, useState } from "react";
import { useToast } from "./components/Toast.jsx";

// Load data on mount / when deps change; exposes reload() for use after mutations.
export function useLoad(fn, deps = []) {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await fn());
    } catch (e) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(() => {
    load();
  }, [load]);
  return { data, loading, reload: load };
}

export const money = (v) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(v || 0));

export const dateFmt = (v) =>
  new Date(v).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
