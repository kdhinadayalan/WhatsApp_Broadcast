import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Contacts from './pages/Contacts';
import Groups from './pages/Groups';
import Templates from './pages/Templates';
import BroadcastComposer from './pages/BroadcastComposer';
import Broadcasts from './pages/Broadcasts';
import BroadcastDetail from './pages/BroadcastDetail';

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/contacts" element={<Contacts />} />
          <Route path="/groups" element={<Groups />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/broadcast/new" element={<BroadcastComposer />} />
          <Route path="/broadcasts" element={<Broadcasts />} />
          <Route path="/broadcasts/:id" element={<BroadcastDetail />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
