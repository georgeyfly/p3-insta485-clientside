import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Button from "./Button";

export default function Like({ postInfo, callApi }) {
  const [numLikesVal, setNumlikesVal] = useState(0);
  const [lognameLikesThis, setLognameLikesThis] = useState(false);

  useEffect(() => {
    if (postInfo && postInfo.likes) {
      setNumlikesVal(postInfo.likes.numLikes);
      setLognameLikesThis(postInfo.likes.lognameLikesThis);
    }
  }, [postInfo]);

  function handleError(response) {
    if (!response.ok) {
      return response.json().then((data) => {
        throw new Error(
          `Server responded with status: ${response.status}. Message: ${data.message}`
        );
      });
    }
    return response;
  }

  function handleLike() {
    const likeUrl = `/api/v1/likes/?postid=${postInfo.postid}`;
    fetch(likeUrl, { method: "POST" })
      .then(handleError)
      .then(() => {
        callApi();
      })
      .catch((error) => {
        console.error("There was an error posting the like:", error);
      });
  }

  function handleDislike() {
    const likeUrl = postInfo.likes.url;
    fetch(likeUrl, { method: "DELETE" })
      .then(handleError)
      .then(() => {
        callApi();
      })
      .catch((error) => {
        console.error("There was an error deleting the like:", error);
      });
  }

  return (
    <div>
      <div>
        {numLikesVal === 1 ? (
          <p>{numLikesVal} like</p>
        ) : (
          <p>{numLikesVal} likes</p>
        )}
      </div>
      {lognameLikesThis ? (
        <Button
          className="like-unlike-button"
          onClick={handleDislike}
          text="dislike"
        />
      ) : (
        <Button
          className="like-unlike-button"
          onClick={handleLike}
          text="like"
        />
      )}
    </div>
  );
}

Like.propTypes = {
  callApi: PropTypes.func.isRequired,
};
