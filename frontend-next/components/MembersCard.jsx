'use client'

// Recent Activity Card:
import { IoPeople } from "react-icons/io5";


export default function MembersCard({members}) {

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5">

      {/* Recent Form Card Heading */}
      <span className="inline-flex items-center gap-3 mb-3 text-3xl font-bold">
        <IoPeople className="text-sky-400"/> Members
      </span>

      <div className="space-y-4">

        {members.map((mem, index) => (
          <div key={index} className="border-l-5 border-sky-500 pl-1 text-[19px]/8 text-zinc-300 mb-3">
            <span className="font-mono font-semibold">
              {mem.full_name}
            </span> <br></br>
            <span className="font-calibiri font-semibold text-sky-800 border rounded-lg p-1">
              {mem.role === 'org_admin'? "Admin" : "Respondent"}
            </span>
          </div>

        ))}
      </div>
    </div>
  );
}