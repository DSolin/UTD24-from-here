import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./index.html", "./src/**/*.{vue,ts,js}"],
  theme: {
    extend: {
      colors: {
        primary: { 50:"#F4F2FF",100:"#E8E4FF",200:"#D1CAFF",300:"#B8ADFF",400:"#A292FF",500:"#8C7CF0",600:"#7360D6",700:"#5B48B0",800:"#45348A",900:"#302462" },
        soft: { pink:"#F0E8FA",lavender:"#E8E0F8",yellow:"#FDF6E3",green:"#E6F7ED",orange:"#FDECE4",sky:"#E3F2FD" },
        accent: { green:"#7DD3A4",yellow:"#F9D068",orange:"#F5A992",coral:"#F08B7C" },
        bg: { primary:"#FAFAFE",card:"#FFFFFF",hover:"#F5F0FD" },
      },
      borderRadius: { card:"18px",button:"12px",tag:"8px",avatar:"50%" },
      boxShadow: { soft:"0 4px 24px rgba(140,124,240,0.10)","soft-hover":"0 8px 32px rgba(140,124,240,0.18)","soft-lg":"0 12px 48px rgba(140,124,240,0.08)",glow:"0 0 20px rgba(140,124,240,0.25)" },
      fontFamily: { sans:['"Inter"','"SF Pro Display"',"-apple-system","sans-serif"], mono:['"JetBrains Mono"',"monospace"] },
      animation: { float:"float 4s ease-in-out infinite","fade-in":"fadeIn 0.6s ease-out","slide-up":"slideUp 0.5s ease-out" },
      keyframes: { float:{"0%,100%":{transform:"translateY(0px)"},"50%":{transform:"translateY(-8px)"}}, fadeIn:{"0%":{opacity:"0"},"100%":{opacity:"1"}}, slideUp:{"0%":{opacity:"0",transform:"translateY(20px)"},"100%":{opacity:"1",transform:"translateY(0)"}} },
    },
  },
  plugins: [],
};
export default config;
