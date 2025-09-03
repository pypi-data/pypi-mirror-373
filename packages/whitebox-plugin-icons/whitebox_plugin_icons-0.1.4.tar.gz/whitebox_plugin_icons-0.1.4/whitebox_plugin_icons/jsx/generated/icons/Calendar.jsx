const Calendar = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={25}
    height={24}
    fill="none"
    {...props}
  >
    <path
      fill="#929292"
      d="M20.5 3h-1V1h-2v2h-10V1h-2v2h-1c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2m0 18h-16V10h16zm0-13h-16V5h16z"
    />
  </svg>
);
export { Calendar };
export default Calendar;

