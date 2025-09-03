const LocationTarget = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={24}
    height={24}
    viewBox="0 0 16 16"
    {...props}
  >
    <path d="M8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4" />
    <path
      fillRule="evenodd"
      d="M2.083 7A6.005 6.005 0 0 1 7 2.083V0h2v2.083A6.005 6.005 0 0 1 13.917 7H16v2h-2.083A6.005 6.005 0 0 1 9 13.917V16H7v-2.083A6.005 6.005 0 0 1 2.083 9H0V7zM4 8a4 4 0 1 1 8 0 4 4 0 0 1-8 0"
      clipRule="evenodd"
    />
  </svg>
);
export { LocationTarget };
export default LocationTarget;

