import React from "react";
import { useState } from "react";
import { useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import useData from "./useData";
import Post from "./Post";

export default function App({ url }) {
  const [currentUrl, setCurrentUrl] = useState(url);
  const [postsInfo, refetch] = useData(currentUrl);
  const [postResults, setPostResults] = useState([]);

  useEffect(() => {
    if (postsInfo) {
      setPostResults((prevPostResults) => [
        ...prevPostResults,
        ...postsInfo.results,
      ]);
    }
  }, [postsInfo]);

  return (
    <InfiniteScroll
      dataLength={postResults.length}
      next={() => {
        setCurrentUrl(postsInfo.next);
      }}
      hasMore={currentUrl ? true : false} // Replace with a condition based on your data source
      loader={<p>Loading...</p>}
      endMessage={<p>No more data to load.</p>}
    >
      <div>
        {postResults.map((postResult) => (
          <Post key={postResult.url} url={postResult.url} />
        ))}
      </div>
    </InfiniteScroll>
  );
}
