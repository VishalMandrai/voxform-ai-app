'use client'

/*
|--------------------------------------------------------------------------
| Welcome Card
|--------------------------------------------------------------------------
*/

import { FcBusinessman } from "react-icons/fc";
import { HiOutlineUserCircle } from "react-icons/hi";


export default function WelcomeCard({ user }) {

  return (

    <div className="border border-white-100 rounded-3xl bg-zinc-900 p-8">
      {/* To compartmentalise the Card internals into 2 parts: */}
      <div className="mt-1 mb-0 grid max-w-9xl items-center gap-3 px-2 lg:grid-cols-[75%_25%]">
        {/* 1. The text part: */}
        <div className="flex flex-col items-center gap-2">
          <p className="text-zinc-400">
            Welcome back 👋
          </p>

          <h1 className="text-4xl font-bold">
            {user.full_name}
          </h1>

          <div className="mt-5 mb-0 flex gap-4">
            <span className="rounded-full bg-zinc-800 px-4 py-2 text-sm text-[18px]">
              {user.org_name}
            </span>
            <span className="rounded-full bg-sky-500/20 px-4 py-2 text-sm text-sky-300 text-[18px]">
              {user.role === "org_admin"
                ? "Organization Admin"
                : "Respondent"}
            </span>
          </div>
          
        </div>
        {/* 2. The Profile Picture part: */}
        <div>
          <HiOutlineUserCircle className="w-50 h-50 text-sky-300/60"/>

          {/* <span className="text-[80px]">
            👋
          </span> */}
        </div>

      </div>

    </div>
  );
}