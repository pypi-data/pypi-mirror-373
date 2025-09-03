const Spinner = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={24} height={24} {...props}>
    <path
      stroke="#fff"
      strokeLinecap="round"
      strokeOpacity={0.1}
      strokeWidth={2.613}
      d="M12.002 4.628A7.376 7.376 0 0 1 19.374 12a7.376 7.376 0 0 1-7.372 7.372A7.376 7.376 0 0 1 4.63 12a7.376 7.376 0 0 1 7.372-7.372Z"
    />
    <path
      stroke="#fff"
      strokeLinecap="round"
      strokeWidth={2.613}
      d="M17.57 16.831a7.38 7.38 0 0 1-9.057 1.66A7.376 7.376 0 0 1 5.51 8.505"
    />
  </svg>
);
export { Spinner };
export default Spinner;

