const StopCircle = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={32}
    height={32}
    fill="none"
    {...props}
  >
    <path
      fill="#EE703B"
      d="M16 2.667C8.64 2.667 2.667 8.64 2.667 16S8.64 29.334 16 29.334 29.333 23.36 29.333 16 23.36 2.667 16 2.667m0 24c-5.893 0-10.667-4.773-10.667-10.667 0-5.893 4.774-10.666 10.667-10.666S26.667 10.107 26.667 16 21.893 26.667 16 26.667m5.333-5.333H10.667V10.667h10.666z"
    />
  </svg>
);
export { StopCircle };
export default StopCircle;

