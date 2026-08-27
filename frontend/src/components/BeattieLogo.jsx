// Simplified recreation of the A.W. Beattie Career Center badge (circular
// bulldog crest with arced lettering and a "Success" ribbon), hand-drawn
// as SVG since no logo file could be attached in this environment.
// Swap for the real artwork if/when a file becomes available.
export default function BeattieLogo({ size = 40, className = "" }) {
  return (
    <svg
      viewBox="0 0 200 200"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-label="A.W. Beattie Career Center"
    >
      <defs>
        <path id="beattie-arc" d="M 22,128 A 78,78 0 1 1 178,128" fill="none" />
      </defs>

      {/* Outer ring */}
      <circle cx="100" cy="100" r="96" fill="#ffffff" stroke="#1c1f26" strokeWidth="6" />
      <circle cx="100" cy="100" r="84" fill="none" stroke="#1c1f26" strokeWidth="2" />

      {/* Arced school name */}
      <text
        fill="#6b2a3a"
        fontFamily="Georgia, 'Times New Roman', serif"
        fontWeight="700"
        fontSize="11.5"
        letterSpacing="0.5"
      >
        <textPath href="#beattie-arc" startOffset="50%" textAnchor="middle">
          A.W. BEATTIE CAREER CENTER
        </textPath>
      </text>

      {/* Bulldog head, simplified but scowling */}
      <g transform="translate(100,110)">
        {/* ears: upright, pointed */}
        <path d="M -44,-30 Q -54,-4 -34,10 Q -34,-16 -18,-30 Z" fill="#9a9fa6" stroke="#1c1f26" strokeWidth="2" />
        <path d="M 44,-30 Q 54,-4 34,10 Q 34,-16 18,-30 Z" fill="#9a9fa6" stroke="#1c1f26" strokeWidth="2" />

        {/* head */}
        <path
          d="M 0,-40
             C 28,-40 46,-20 46,0
             C 46,14 40,22 36,28
             C 42,34 42,44 34,48
             C 22,54 -22,54 -34,48
             C -42,44 -42,34 -36,28
             C -40,22 -46,14 -46,0
             C -46,-20 -28,-40 0,-40 Z"
          fill="#cfd3d6"
          stroke="#1c1f26"
          strokeWidth="2.5"
        />

        {/* angry brow */}
        <path d="M -32,-4 L -10,4" stroke="#1c1f26" strokeWidth="4" strokeLinecap="round" />
        <path d="M 32,-4 L 10,4" stroke="#1c1f26" strokeWidth="4" strokeLinecap="round" />
        <path d="M -30,-14 Q 0,-6 30,-14" fill="none" stroke="#9a9fa6" strokeWidth="3" strokeLinecap="round" />

        {/* eyes: narrowed */}
        <ellipse cx="-15" cy="4" rx="4.5" ry="3.2" fill="#1c1f26" />
        <ellipse cx="15" cy="4" rx="4.5" ry="3.2" fill="#1c1f26" />

        {/* jowls / muzzle, heavier + wrinkled */}
        <path
          d="M -24,14 Q -30,36 -12,44 Q 0,47 0,47 Q 0,47 12,44 Q 30,36 24,14
             Q 13,26 0,26 Q -13,26 -24,14 Z"
          fill="#e6e8ea"
          stroke="#1c1f26"
          strokeWidth="2"
        />
        <path d="M -20,20 Q -14,26 -6,26" fill="none" stroke="#b7bbbf" strokeWidth="1.5" />
        <path d="M 20,20 Q 14,26 6,26" fill="none" stroke="#b7bbbf" strokeWidth="1.5" />

        {/* nose */}
        <ellipse cx="0" cy="14" rx="8.5" ry="5.5" fill="#1c1f26" />

        {/* underbite mouth */}
        <path d="M 0,19 Q 0,30 -12,34" fill="none" stroke="#1c1f26" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M 0,19 Q 0,30 12,34" fill="none" stroke="#1c1f26" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M -7,32 L -3,38 L 1,32" fill="#ffffff" stroke="#1c1f26" strokeWidth="1.5" />

        {/* collar */}
        <path d="M -28,44 Q 0,56 28,44 L 28,52 Q 0,64 -28,52 Z" fill="#6b2a3a" />
      </g>

      {/* Ribbon */}
      <g transform="translate(100,170)">
        <path d="M -70,-10 L -46,4 L -70,16 Z" fill="#551f2c" />
        <path d="M 70,-10 L 46,4 L 70,16 Z" fill="#551f2c" />
        <rect x="-46" y="-10" width="92" height="26" fill="#6b2a3a" />
        <text
          x="0"
          y="8"
          textAnchor="middle"
          fill="#ffffff"
          fontFamily="Georgia, 'Times New Roman', serif"
          fontStyle="italic"
          fontWeight="600"
          fontSize="15"
        >
          Success
        </text>
      </g>
    </svg>
  );
}
