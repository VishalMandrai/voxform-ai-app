import { GrAdd } from "react-icons/gr";
import { IoReload } from "react-icons/io5";
import { GiEclipseFlare } from "react-icons/gi";
import { RiUserVoiceLine } from "react-icons/ri";
import { GiIncomingRocket } from "react-icons/gi";

import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";

export default function BuilderToolbar(props) {
    const navigation = useRouter()

    const pathname = usePathname();
    const NoEditForm = pathname.startsWith("/builder");

    return (
        <div className="inline-flex items-center gap-4 px-2 py-5">

            {/* New form button routing based on User Location: */}
            {NoEditForm ?
                <button className="flex items-center gap-2 rounded-lg bg-[#4aafaf] border border-white px-4 py-2 text-black text-bold hover:bg-[#13333d] hover:text-white"
                onClick={props.reloadBuilder}>
                <IoReload /> Reset Form
            </button>
                :
                <button className="flex items-center gap-2 rounded-lg bg-[#4aafaf] px-4 py-2 text-black text-bold hover:bg-[#13333d] hover:text-white"
            onClick={() => navigation.push("/builder")}>
                <GrAdd /> New Form
            </button>
            }


            {/* Features to be added next: */}
            <button className="group flex items-center gap-2 rounded-lg border 
                               px-4 py-2 hover:bg-[#316b7e]">
                <span className="group-hover:hidden flex items-center gap-2"> 
                    <GiEclipseFlare /> AI Generate
                </span>
                <span className="hidden group-hover:flex items-center gap-2">
                    <GiIncomingRocket /> Coming Soon...
                </span>
            </button>

            <button className="group flex items-center gap-2 rounded-lg border 
                               px-4 py-2 hover:bg-[#316b7e]">
                <span className="group-hover:hidden flex items-center gap-2"> 
                    <RiUserVoiceLine /> Voice Test
                </span>
                <span className="hidden group-hover:flex items-center gap-2">
                    <GiIncomingRocket /> Coming Soon...
                </span>
            </button>

        </div>
    );
}