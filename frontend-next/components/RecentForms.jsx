'use client'

// Recent Forms
import { useRef } from 'react';
import { BsStars } from "react-icons/bs";
import { FaHashtag } from "react-icons/fa";

export default function RecentForms({forms}) {

    const trayRef = useRef(null);

    const scroll = (direction) => {
      if (trayRef.current) {
        const { scrollLeft, clientWidth } = trayRef.current;
        // Scroll by the width of one visible view area
        const scrollTo = direction === 'left' 
          ? scrollLeft - clientWidth 
          : scrollLeft + clientWidth;
        
        trayRef.current.scrollTo({ left: scrollTo, behavior: 'smooth' });
      };
    }

  return (
      <div className="relative flex-col items-center rounded-2xl border border-zinc-800 bg-zinc-900 p-6 
                      w-full max-w-7xl mx-auto px-10 box-border">

        {/* Recent Form Card Heading */}
        <span className="inline-flex items-center gap-3 mb-3 text-3xl font-bold">
          <BsStars className="text-sky-400"/> Recent Forms
        </span>

        <div className="space-y-3">
          {/* Left Navigation Button */}
          <button 
            onClick={() => scroll('left')} 
            className="absolute left-0 top-1/2 -translate-y-1/2
                      text-sky-400 rounded-lg w-10 h-10 text-6xl font-medium
                      flex items-center justify-center z-10 shadow-md 
                      cursor-pointer transition-colors"
          >
            &#8249;
          </button>
          
          {/* Slider Tray */}
          <div 
            ref={trayRef} 
            className="flex gap-14 overflow-x-auto scroll-smooth w-full px-7
                      py-5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">

            {/* Form Card */}
            {forms.map((form, index) => (
              <div 
                key={form.form_id} 
                className="flex-shrink-0 w-full sm:w-[calc(50%-10px)] md:w-[calc(33.333%-14px)] 
                          min-w-[500px] bg-zinc-800 border border-gray-600 rounded-xl p-4 shadow-sm 
                          transition hover:bg-zinc-900">

                <span className="inline-flex items-center gap-0 text-[24px] font-semibold 
                                text-sky-600 m-0 mb-3 p-2 border rounded-lg border-gray-600">
                  <FaHashtag /> {index + 1}
                  <span className="px-3 text-white">
                    {form.title}
                  </span>
                </span>

                <br></br>

                <span className="text-xl text-zinc-300 mb-5">{form.description}</span>

                <br></br>
                <br></br>

                <span className="inline-flex items-center gap-10 text-[20px]/10 font-semibold 
                                text-sky-600 m-0 p-2">
                  <span className="border rounded-lg border-gray-600 p-4 text-zinc-400">
                    Total Responses <br></br>
                    <span className="text-white text-[22px]">{form.response_count}</span>
                  </span>

                  <span className="border rounded-lg border-gray-600 p-4 text-zinc-400">
                    Last Response <br></br>
                    <span className="text-white text-[22px]">
                     {form.last_response_at ? new Date(form.last_response_at).toDateString() : "..."}
                    </span>
                  </span>

                </span>

              </div>
            ))}

          </div>

          {/* Right Navigation Button */}
          <button 
            onClick={() => scroll('right')} 
            className="absolute right-0 top-1/2 -translate-y-1/2 
                      text-sky-400 rounded-lg w-10 h-10 text-6xl font-medium
                      flex items-center justify-center z-10 shadow-md 
                      cursor-pointer transition-colors">
            &#8250;
          </button>

        </div>

      </div>
  );

}