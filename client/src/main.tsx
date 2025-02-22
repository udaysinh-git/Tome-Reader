import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

import "@ionic/react/css/core.css";

import { MainPage } from "./Main/MainPage.tsx";

import { IonApp, setupIonicReact } from "@ionic/react";

import { BrowserRouter } from "react-router-dom";

setupIonicReact({
  mode: "ios",
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
