// SurveyConfig.jsx

import { Serializer } from "survey-core";

// ALL SURVEY-JS SETTING NOBES

Serializer.getProperty("survey", "showQuestionNumbers").visible = false;
Serializer.getProperty("question", "correctAnswer").visible = false;
Serializer.getProperty("question", "isRequired").visible = true;
Serializer.findProperty("question", "correctAnswer").visible = false;
Serializer.findProperty("question", "defaultValueExpression").visible = false;

Serializer.getProperty("survey", "logo").visible = false;
Serializer.getProperty("survey", "logoWidth").visible = false;
Serializer.getProperty("survey", "logoHeight").visible = false;
Serializer.getProperty("survey", "logoFit").visible = false;


// Hide Validation Tab - from all the following question types
[
    "text",
    "comment",
    "radiogroup",
    "checkbox",
    "dropdown",
    "matrix",
].forEach(type => {
    const prop = Serializer.findProperty(type, "validators");
    if (prop) prop.visible = false;
});


// Hide Conditions
[
  "visibleIf",
  "enableIf",
  "requiredIf"
].forEach(name => {
    const prop = Serializer.findProperty("question", name);
    if (prop) prop.visible = false;
});