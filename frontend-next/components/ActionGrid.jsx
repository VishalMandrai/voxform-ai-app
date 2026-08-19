'use client'

// Action Grid:

import { FaMicrophoneAlt } from "react-icons/fa";
import { FaClipboardList } from "react-icons/fa";
import { CgTemplate } from "react-icons/cg";
import { IoBarChartOutline } from "react-icons/io5";
import { MdInsertInvitation } from "react-icons/md";


import ActionCard from "./ActionCard";

export default function ActionGrid({ isAdmin }) {

  return (

    <div className="grid flex text-center gap-6 md:grid-cols-2 xl:grid-cols-4">

      <ActionCard
        icon={FaClipboardList}
        title="Fill Forms"
        description="Open available forms and submit responses."
        to="/forms"
        open={true}
      />

      {isAdmin && (

        <>
          <ActionCard
            icon={CgTemplate}
            title="Build Forms"
            description="Create new AI-powered forms."
            to="/builder"
            open={true}
          />

          <ActionCard
            icon={IoBarChartOutline}
            title="Analytics"
            description="View response analytics."
            to=""
            open={false}
          />

          <ActionCard
            icon={MdInsertInvitation}
            title="Invite"
            description="Add new respondents to organization."
            to="/invite"
            open={true}
          />
        </>

      )}

    </div>

  );

}