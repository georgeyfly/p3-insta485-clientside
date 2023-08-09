import { useState, useEffect } from "react";

export default function useData(url) {
  const [data, setData] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);
  useEffect(() => {
    if (url) {
      let ignore = false;
      fetch(url)
        .then((response) => response.json())
        .then((json) => {
          if (!ignore) {
            setData(json);
          }
        });
      return () => {
        ignore = true;
      };
    }
  }, [url, refreshCount]);

  const refetch = () => {
    setRefreshCount((prev) => prev + 1);
  };

  return [data, refetch];
}
