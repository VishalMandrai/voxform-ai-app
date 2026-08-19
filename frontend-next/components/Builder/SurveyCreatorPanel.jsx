'use client'

import { useState, useEffect} from "react";

import { SurveyCreatorComponent, SurveyCreator } from "survey-creator-react";
import "./SurveyConfig";

import "survey-core/survey-core.css";
import "survey-creator-core/survey-creator-core.css";
import "survey-core/survey.i18n";
import "survey-creator-core/survey-creator-core.i18n";

// Enable Ace Editor in the JSON Editor tab
import "ace-builds/src-noconflict/ace";
import "ace-builds/src-noconflict/ext-searchbox";

// Custom Survey Creator Theme as per VoxForm look:
import "./themes/survey-creator-theme.css"

// New Survey theme for VoxForm {for Preview Tab + Form Fill} 
import voxformTheme from "./themes/survey_theme";

// Axios function for API POST Call for Form JSON Dump
import { SaveForm } from "@/api/forms"


const defaultCreatorOptions = {
  autoSaveEnabled: false,
  showSaveButton: true,  // Forces the built-in save button to appear in the toolbar
  showLogicTab: false,
  showTranslationTab: false,
  // showThemeTab: true,
  showSidebar: false,

};

const remove_tools = ["matrixdropdown", "panel", "paneldynamic", "html", "expression", 
  "image", "signaturepad", "file", "matrixdynamic"];

const defaultJson = {
  title: "",
  description: "",
  pages: [{
    elements: [{
      title: "Enter your first name:",
      type: "text"
    }, {
      title: "Enter your last name:",
      type: "text"
    }]
  }]
};

export default function SurveyCreatorWidget(props) {
  const [creator, setCreator] = useState(null);

  useEffect(() => {
    // Create the creator
    const c = new SurveyCreator(props.options || defaultCreatorOptions);
    
    // Adding custom theme to creator object 
    c.theme = voxformTheme;

    // Keeping only allowed tools from all available tools & removing the rest:
    remove_tools.map((tool) => (c.toolbox.removeItem(tool)));

    // Load initial JSON data into the creator panel
    c.text = JSON.stringify(props.json) || JSON.stringify(defaultJson);

    // Define the click function for the built-in Save button
    // Setup the async save routine using Axios
    c.saveSurveyFunc = async (saveNo, callback) => {
      console.log(c.JSON);
      try {
        // Await your custom Axios API function wrapper
        const response = await SaveForm(c.JSON);
        
        // SurveyJS expects callback(saveNo, true) on HTTP 2xx success
        callback(saveNo, true);
        alert(`New Form "${c.JSON.title}" saved successfully!`);
        
      } catch (error) {
        console.error("Axios save error:", error);
        
        // callback(saveNo, false) keeps the save button clickable if the request fails
        callback(saveNo, false);
        alert("Failed to save survey. Please check your connection.");
      }
    };

    setCreator(c);

}, [props.options]);

  if (!creator)
    return (
      <div style={{ height: "100vh", width: "100%" }}>
        <p>
          Loading the Survey Creator....
        </p>
      </div>
    );


  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <SurveyCreatorComponent creator={creator} />
    </div>
  );
}
