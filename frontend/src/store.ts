import { create } from 'zustand';

interface State {
  modelName: string;
  setModelName: (name: string) => void;
}

const useStore = create<State>((set) => ({
  modelName: '',
  setModelName: (name) => set({ modelName: name }),
}));

export default useStore;
