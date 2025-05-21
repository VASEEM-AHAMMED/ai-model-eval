import useStore from '../store';

export default function Upload() {
  const { modelName, setModelName } = useStore();

  return (
    <div>
      <h1>Upload Model</h1>
      <input
        type="text"
        value={modelName}
        onChange={(e) => setModelName(e.target.value)}
        placeholder="Model Name"
      />
      <p>Model Name: {modelName}</p>
    </div>
  );
}
