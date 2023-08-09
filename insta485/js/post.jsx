import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from "moment";
import Likes from "./Likes";
import useData from "./useData";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");

  const [postInfo, ] = useData(url);
  useEffect(() => {
    if (postInfo) {
      setImgUrl(postInfo.imgUrl);
      setOwner(postInfo.owner);
      setOwnerImgUrl(postInfo.ownerImgUrl);
      setTimestamp(moment(postInfo.created, "YYYY-MM-DD HH:mm:ss").fromNow());
      setPostShowUrl(postInfo.postShowUrl);
      setOwnerShowUrl(postInfo.ownerShowUrl);
    }
  }, [postInfo]);

  // Render post image and post owner
  return (
    <div className="post">
      <a href={ownerShowUrl}>
        <img className="profile_img" src={ownerImgUrl} alt="owner_image" />
      </a>
      <p>
        <a href={ownerShowUrl}>{owner}</a>
      </p>
      <img className="post_img" src={imgUrl} alt="post_image" />
      <div>
        <a href={postShowUrl}>{timestamp}</a>
      </div>
      <Likes url={url} />
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
