import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Button from "./Button";

import useData from "./useData";

export default function Likes({ url }){
    const [numLikesVal, setNumlikesVal] = useState(0);
    const [lognameLikesThis, setLognameLikesThis] = useState(false);
    const [postInfo, refetch] = useData(url);
    
    useEffect(() => {
      if (postInfo && postInfo.likes) {
        setNumlikesVal(postInfo.likes.numLikes);
        setLognameLikesThis(postInfo.likes.lognameLikesThis);
      }
    }, [postInfo]);

    function handleLike() {
      const likeUrl = "/api/v1/likes/" + "?postid=" + postInfo.postid;
      // Send a POST request to the like's URL
      fetch(likeUrl, {
        method: "POST",
      })
        .then((response) => {
          if (response.status === 201) {
            setNumlikesVal((prevNumLikes) => prevNumLikes + 1);
            setLognameLikesThis(true);
            refetch();
          } else {
            return response.json().then((data) => {
              throw new Error(
                `Server responded with status: ${response.status}. Message: ${data.message}`
              );
            });
          }
        })
        .catch((error) => {
          console.error("There was an error posting the like:", error);
        });
    }
    
    function handleDislike() {
      const likeUrl = postInfo.likes.url;
      // Send a DELETE request to the like's URL
      fetch(likeUrl, {
        method: "DELETE",
      })
        .then((response) => {
          if (response.status === 204) {
            setNumlikesVal((prevNumLikes) => prevNumLikes - 1);
            setLognameLikesThis(false);
            refetch();
          } else {
            return response.json().then((data) => {
              throw new Error(
                `Server responded with status: ${response.status}. Message: ${data.message}`
              );
            });
          }
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
