import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Button from "./Button";

export default function Comment({ postInfo, callApi }) {
  const [comments, setComments] = useState([]);
  const [textEntry, setTextEntry] = useState("");
  const [, setNewComment] = useState(null);

  useEffect(() => {
    if (postInfo && postInfo.comments) {
      setComments(postInfo.comments);
    }
  }, [postInfo]);

  // function called when user types in text field
  const handleChange = (event) => {
    setTextEntry(event.target.value);
  };

  // error handle
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
  // function called when user submits
  const handleSubmit = (event) => {
    const commentUrl = `/api/v1/comments/?postid=${postInfo.postid}`;
    fetch(commentUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: textEntry }),
    })
      .then(handleError)
      .then(() => {
        setNewComment(textEntry);
        callApi();
      })
      .catch((error) => {
        console.error("There was an error posting the comments:", error);
      });
    // prevents website from refreshing (default action of form submission)
    event.preventDefault();
  };

  const handleDelete = (commentid) => {
    const commentUrl = `/api/v1/comments/${commentid}`;
    fetch(commentUrl, {
      method: "DELETE",
    })
      .then(handleError)
      .then(() => {
        callApi();
      })
      .catch((error) => {
        console.error("There was an error posting the comments:", error);
      });
  };

  return (
    <div>
      <div>
        {comments.map((comment) => (
          <div key={comment.commentid}>
            <a href={comment.ownerShowUrl}>
              <strong>{comment.owner}</strong>
            </a>
            <span className="comment-text"> {comment.text} </span>
            {comment.lognameOwnsThis && (
              <Button
                className="delete-comment-button"
                onClick={() => handleDelete(comment.commentid)}
                text="Delete Component"
              />
            )}
          </div>
        ))}
      </div>
      <form className="comment-form" onSubmit={handleSubmit}>
        <input type="text" value={textEntry} onChange={handleChange} />
      </form>
    </div>
  );
}

Comment.propTypes = {
  // postInfo: PropTypes.shape({
  //   comments: PropTypes.arrayOf(
  //     PropTypes.shape({
  //       commentid: PropTypes.number,
  //       lognameOwnsThis: PropTypes.bool,
  //       owner: PropTypes.string,
  //       ownerShowUrl: PropTypes.string,
  //       text: PropTypes.string,
  //       url: PropTypes.string,
  //     })
  //   ).isRequired,
  //   comments_url: PropTypes.string,
  //   created: PropTypes.string,
  //   imgUrl: PropTypes.string,
  //   likes: PropTypes.shape({
  //     lognameLikesThis: PropTypes.bool,
  //     numLikes: PropTypes.number,
  //     url: PropTypes.string,
  //   }).isRequired,
  //   owner: PropTypes.string,
  //   ownerImgUrl: PropTypes.string,
  //   ownerShowUrl: PropTypes.string,
  //   postShowUrl: PropTypes.string,
  //   postid: PropTypes.number,
  //   url: PropTypes.string,
  // }).isRequired,
  callApi: PropTypes.func.isRequired,
};
