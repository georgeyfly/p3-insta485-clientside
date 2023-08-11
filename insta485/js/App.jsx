import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import PropTypes from "prop-types";
import useData from "./useData";
import Post from "./Post";

export default function App({ url }) {
  const [currentUrl, setCurrentUrl] = useState(url);
  const [postsInfo, ,] = useData(currentUrl);
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
      hasMore={!!currentUrl} // Replace with a condition based on your data source
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

App.propTypes = {
  url: PropTypes.string.isRequired,
};
