import WhiteButton from "./components/whiteButton";
import TextBox from "./components/textBox";

const Home: React.FC = () => {
  return (
    <div className="bg-black w-screen h-screen flex flex-col justify-center items-center">
      <TextBox />
      <div className="my-10"> 
        <WhiteButton />
      </div>
    </div>
  );
};

export default Home;

