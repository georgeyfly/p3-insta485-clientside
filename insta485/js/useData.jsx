import { useState, useEffect } from "react";

export default function useData(url) {
  const [data, setData] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (url) {
      let ignore = false;
      fetch(url)
        .then((response) => response.json())
        .then((json) => {
          if (!ignore) {
            setData(json);
            setLoading(false);
          }
        });
      return () => {
        ignore = true;
      };
    }
    return () => {}; // No-op function for when url is not present for eslint pass
  }, [url, refreshCount]);

  const refetch = () => {
    setRefreshCount((prev) => prev + 1);
    setLoading(true);
  };

  return [data, refetch, loading];
}
