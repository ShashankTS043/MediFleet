import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/App.css";
import Layout from "@/components/Layout";
import Home from "@/pages/Home";
import CreateTask from "@/pages/CreateTask";
import Dashboard from "@/pages/Dashboard";
import Robots from "@/pages/Robots";
import Analytics from "@/pages/Analytics";
import About from "@/pages/About";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="create-task" element={<CreateTask />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="robots" element={<Robots />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="about" element={<About />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;