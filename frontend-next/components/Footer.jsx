/*
|--------------------------------------------------------------------------
| Footer
|--------------------------------------------------------------------------
*/

import Link from 'next/link'
import Metadata from './Metadata'
import SocialIcon from './social-icons'

export default function Footer() {
  return (
    <footer>
      <div className="mt-16 flex flex-col items-center">
        <div className="mb-3 flex space-x-4">
          <SocialIcon kind="mail" href={`mailto:${Metadata.email}`} />
          <SocialIcon kind="github" href={Metadata.github} />
          <SocialIcon kind="linkedin" href={Metadata.linkedin} />
        </div>
        <div className="mb-2 flex space-x-2 text-sm text-gray-400">
          <div>{Metadata.author}</div>
          <div>{` • `}</div>
          <div>{`© ${new Date().getFullYear()}`}</div>
          <div>{` • `}</div>
          <Link href="/">{Metadata.title}</Link>
        </div>
      </div>
    </footer>
  )
}
