'use client'

import { Fragment, useEffect, useRef, useState } from 'react'
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";
import Link from 'next/link';
import Image from 'next/image';

import { IoLogOutOutline } from "react-icons/io5";

import HeaderNavLinks from '@/components/HeaderNavLinks'
import Logo from '@/public/voxform-logo.svg'
import SectionContainer from '@/components/SectionContainer'
import Footer from '@/components/Footer'

import { logout } from '@/api/auth';


const LayoutWrapper = ({children}) => {
  // To bypass SectionCaontainer for Builder Page
  const pathname = usePathname();
  const navigate = useRouter();

  // We don't want SectionContainer Component for few pages 
  const NoSectionContainer = pathname.startsWith("/builder") || pathname.startsWith("/fillform") || pathname.startsWith("/edit-form") || pathname.startsWith("/about");
  
  const [stuck, setStuck] = useState(false)
  const ref = useRef()

  const stuckClasses = 'py-2 sticky top-n-1 z-50 transition-all backdrop isSticky mx-auto border-b border-slate-300/10 mb-8 w-full'
  const unstuckClasses = 'py-2 md:py-4 sticky top-n-1 z-50 transition-all backdrop mx-auto border-b border-b-0 border-slate-300/10 mb-2 w-full'
  
  const classes = stuck ? stuckClasses : unstuckClasses


  useEffect(() => {
    const cachedRef = ref.current
    const observer = new IntersectionObserver(
      ([e]) => {
        setStuck(e.intersectionRatio < 1)
      },
      { threshold: [1.0] }
    )
    observer.observe(cachedRef)
    return () => observer.unobserve(cachedRef)
  }, [ref]);

  // Function that creates a Duplicate form on single click
    const logOut = async () => {
      try {
        // 1. Trigger Log-out
        const response = await logout();

        // 2. Navigate to App Landing Page
        navigate.push('/');

      } catch (err) {
        console.error(err);
        alert("Unable to Log-out.");

      }
    };


  return (
    <>
      <header id="main-wrapper" className={classes} ref={ref}>
        
        {/* Decorative background glows */}
        {/* <BackgroundGlow /> */}
        
        {/* ------------- App Logo -------------- */}
        <div className="mt-1 mx-auto flex max-w-5xl items-center justify-between bg-cardBg bg-opacity-5 px-2 sm:px-2 xl:max-w-5xl xl:px-0">
            <div className = "mr-3">
              <Link href="/" aria-label="VoxForm AI">
                <Image 
                  src={Logo} 
                  alt="App logo" 
                  width={250} // Set appropriate dimensions
                  height={100}
                />
              </Link>
            </div>
          {/* ------------ Nav Tabs ------------- */}
          <div className="flex items-center text-xl leading-2">
            <div className="hidden sm:block">
              {HeaderNavLinks.map((link) => {
                  return (
                    <a
                      key={link.title}
                      href={link.href}
                      className="p-1 font-bold text-gray-100 text-[20px] hover:text-primary-400 sm:p-4 
                                cursor:pointer"
                    >
                      {link.title}
                    </a>
                  )
              })}
            </div>
            {/* --------- Log-out Button ---------- */}
            {(pathname !== '/') && (!pathname.startsWith("/sign-up")) ? (
              <button
                className="m-0 py-2 px-2 font-bold text-gray-100 text-[20px] 
                          hover:text-primary-400 cursor-pointer"
                onClick={logOut}
              >
                <IoLogOutOutline className="w-8 h-8 py-0"/>
              </button>
            ) : (<button className="m-0 py-0 pt-0 px-0 font-bold text-gray-100 text-[1px] 
                          hover:text-primary-400"></button>)
            }
          </div>
        </div>
      </header>
      {NoSectionContainer ? (
        <main className="">
            {children}
        </main>
            ) : (
                <SectionContainer>
                  <main className="mb-auto">
                      {children}
                  </main>
                  <Footer />
                </SectionContainer>
            )}
    </>
  )
}

export default LayoutWrapper



/*
|--------------------------------------------------------------------------
| Background blurred circles
|--------------------------------------------------------------------------
*/

function BackgroundGlow() {
  return (
    <>
      <div className="absolute z-0 left-[0px] top-[0px] h-[300px] w-[300px] rounded-full bg-white-500/80 blur-[180px]" />

      <div className="absolute z-0 right-[0px] top-[0px] h-[300px] w-[300px] rounded-full bg-cyan-500/10 blur-[180px]" />
    </>
  );
}
