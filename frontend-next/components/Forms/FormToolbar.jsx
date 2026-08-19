import { GrAdd } from "react-icons/gr";
import { GiEclipseFlare } from "react-icons/gi";
import { RiUserVoiceLine } from "react-icons/ri";

import { useRouter } from 'next/navigation';


export default function FormToolbar({form_id}) {
    
    const navigate = useRouter();
    
    return (
        <div className="inline-flex items-center gap-4 px-2 py-4">

            {/* A button will open window to Edit the currently openend form */}
            <button className="flex items-center gap-2 rounded-lg bg-[#4aafaf] px-4 py-2 text-lg 
                            text-black text-bold hover:bg-[#13333d] hover:text-white"
                            onClick={() => navigate.push(`/edit-form?id=${form_id}`)}>
                <span className="text-lg"><GrAdd /></span> Edit Form
            </button>

            {/* A button will open window to create new form */}
            <button className="flex items-center gap-2 rounded-lg border px-4 py-2 text-lg 
                    hover:bg-[#316b7e]"
                    onClick={() => navigate.push("/builder")}
                    >
                <span className="text-lg"><GiEclipseFlare /></span> Build New
            </button>

            {/* <button className="flex items-center gap-2 rounded-lg border px-4 py-2 hover:bg-[#316b7e]">
                <RiUserVoiceLine /> Voice Test
            </button> */}

        </div>
    );
}