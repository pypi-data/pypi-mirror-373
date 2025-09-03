const PlayCircle = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={32}
    height={32}
    fill="none"
    {...props}
  >
    <path
      fill="#181818"
      d="M16 2.667C8.64 2.667 2.667 8.64 2.667 16S8.64 29.334 16 29.334 29.333 23.36 29.333 16 23.36 2.667 16 2.667m0 24C10.12 26.667 5.333 21.88 5.333 16S10.12 5.334 16 5.334 26.667 10.12 26.667 16 21.88 26.667 16 26.667M12.667 22 22 16l-9.333-6z"
    />
  </svg>
);
export { PlayCircle };
export default PlayCircle;

