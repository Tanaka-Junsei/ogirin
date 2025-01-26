import { useState } from 'react';
import styles from '../styles/Home.module.css';

export default function Home() {
  const [description, setDescription] = useState('大喜利のお題をAIを使って生成します');
  const [buttonText, setButtonText] = useState('お題を生成');
  const [isLoading, setIsLoading] = useState(false);

  const handleButtonClick = () => {
    setIsLoading(true); // ローディング状態を開始
    setDescription('お題生成中...'); // 説明文をローディング中に変更

    setTimeout(() => {
      setIsLoading(false); // ローディング状態を終了
      setDescription('お題が生成されました！');
      setButtonText('再度生成する');
    }, 10000); // 10秒後に実行
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>大喜林</h1>
      <p className={styles.description}>{description}</p>

      {isLoading ? (
        <div className={styles.spinner}></div>
      ) : (
        <button className={styles.button} onClick={handleButtonClick}>
          {buttonText}
        </button>
      )}
    </div>
  );
}
