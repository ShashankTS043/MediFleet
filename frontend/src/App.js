import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/App.css";
import Layout from "@/components/Layout";
import Home from "@/pages/Home";
import CreateTask from "@/pages/CreateTask";
import Dashboard from "@/pages/Dashboard";
import Robots from "@/pages/Robots";
import Analytics from "@/pages/Analytics";
import About from "@/pages/About";
import MQTTDocs from "@/pages/MQTTDocs";
import APIDocs from "@/pages/APIDocs";

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
          <Route path="mqtt-docs" element={<MQTTDocs />} />
          <Route path="api-docs" element={<APIDocs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;