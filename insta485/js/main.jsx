import React from "react";
import { createRoot } from "react-dom/client";
import Post from "./Post";
import App from "./App";

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

// This method is only called once
// Insert the post component into the DOM
root.render(
  <App url="/api/v1/posts/" />
  );
