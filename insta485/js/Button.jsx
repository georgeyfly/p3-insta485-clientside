import React from "react";
import PropTypes from "prop-types";

export default function Button({ className, onClick, text }) {
  return (
    <button className="className" type="button" onClick={onClick}>
      {text}
    </button>
  );
}

Button.propTypes = {
  onClick: PropTypes.func.isRequired,
  text: PropTypes.string.isRequired,
};
