'use client'

// Action Card in Action Grid:

// NEXT Equivalent of -> import { useNavigate } from "react-router-dom";
import { useRouter } from 'next/navigation';

import { GiIncomingRocket } from "react-icons/gi";


export default function ActionCard({
  icon: Icon,
  title,
  description,
  to,
  open
}) {

  const navigate = useRouter();

  return (
    <>
      {open ? (
          <main onClick={() => navigate.push(to)} className="m-0 p-0">
            <button
              className="flex flex-col justify-start rounded-2xl min-h-70 min-w-50 border border-zinc-800 
              bg-zinc-900 p-3 text-left transition hover:border-sky-500 hover:bg-zinc-800 cursor-pointer"
            >
              <div className="mt-10 flex flex-col items-center">
                <div className="inline-flex items-center gap-3 mb-7">
                  <Icon className="h-10 w-10 text-sky-400" /> 

                  <span className="text-2xl font-semibold">
                    {title}
                  </span>
                </div>
              </div>
              
              <div className="items-center text-sm text-zinc-400 text-center">
                <span className="text-xl font-medium">
                  {description}
                </span>
              </div>

            </button>
          </main>
          ) : (
            <main className="m-0 p-0">
              <button
                className="group flex flex-col justify-start rounded-2xl min-h-70 min-w-50 border 
                          border-zinc-800 bg-zinc-900 p-3 text-left transition cursor-pointer
                          hover:border-sky-500 hover:bg-zinc-800">
                <span className="group-hover:hidden">
                  <div className="mt-10 flex flex-col items-center">
                    <div className="inline-flex items-center gap-3 mb-7">
                      <Icon className="h-10 w-10 text-sky-400" /> 

                      <span className="text-2xl font-semibold">
                        {title}
                      </span>
                    </div>
                  </div>
                  
                  <div className="items-center text-sm text-zinc-400 text-center">
                    <span className="text-xl font-medium">
                      {description}
                    </span>
                  </div>
                </span>

                <span className="hidden group-hover:inline">
                  <div className="mt-22 flex items-center gap-3 mb-7">
                    <GiIncomingRocket className="h-10 w-10 text-sky-400" /> 

                    <span className="text-2xl font-semibold">
                      New Feature. Coming Soon!
                    </span>
                  </div>
                </span>

              </button>
            </main>
          )
      }
    </>
  );

}