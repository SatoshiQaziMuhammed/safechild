import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'; // Direct axios for admin stats specific call if not in service
import { useAuth } from '../contexts/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';

// Assuming base API URL is handled or we use the instance from lib/api
import api from '../lib/api'; 

const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    activeClients: 0,
    processingCases: 0,
    completedCases: 0,
    totalMeetings: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/admin/stats');
        setStats(res.data);
      } catch (err) {
        console.error("Failed to fetch admin stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
            <p className="text-gray-600">Welcome back, {user?.firstName || 'Admin'}</p>
          </div>
          <div className="space-x-4">
            <Link 
              to="/admin/clients" 
              className="bg-white border border-gray-300 text-gray-700 font-bold py-2 px-4 rounded-lg shadow-sm hover:bg-gray-50"
            >
              Manage Clients
            </Link>
            <Link 
              to="/admin/forensics" 
              className="bg-blue-900 hover:bg-blue-800 text-white font-bold py-2 px-4 rounded-lg shadow-md"
            >
              Forensic Tools
            </Link>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
          <StatCard 
            title="Active Clients" 
            value={stats.activeClients} 
            icon="👥" 
            color="blue"
            link="/admin/clients"
          />
          <StatCard 
            title="Pending Evidence" 
            value={stats.processingCases} 
            icon="⏳" 
            color="yellow"
            link="/admin/forensics"
          />
          <StatCard 
            title="Completed Reports" 
            value={stats.completedCases} 
            icon="✅" 
            color="green"
            link="/admin/forensics"
          />
          <StatCard 
            title="Scheduled Meetings" 
            value={stats.scheduledMeetings || 0} 
            icon="📅" 
            color="purple"
            link="/admin/meetings"
          />
        </div>

        {/* Quick Actions & Info */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Quick Actions Panel */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 gap-4">
              <Link to="/admin/forensics" className="p-4 border border-blue-100 bg-blue-50 rounded-lg hover:bg-blue-100 transition text-center group">
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">🪄</div>
                <div className="font-bold text-blue-900">Create Magic Link</div>
                <div className="text-xs text-blue-700">Request evidence via URL</div>
              </Link>
              
              <Link to="/admin/clients" className="p-4 border border-gray-100 bg-gray-50 rounded-lg hover:bg-gray-100 transition text-center group">
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">👤</div>
                <div className="font-bold text-gray-800">Add New Client</div>
                <div className="text-xs text-gray-500">Register a new case file</div>
              </Link>

              <Link to="/whatsapp-connect" className="p-4 border border-green-100 bg-green-50 rounded-lg hover:bg-green-100 transition text-center group">
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">📱</div>
                <div className="font-bold text-green-900">Social Extract</div>
                <div className="text-xs text-green-700">WhatsApp / Telegram Tool</div>
              </Link>

              <div className="p-4 border border-purple-100 bg-purple-50 rounded-lg hover:bg-purple-100 transition text-center group cursor-pointer">
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">📊</div>
                <div className="font-bold text-purple-900">Financials</div>
                <div className="text-xs text-purple-700">View payment history</div>
              </div>
            </div>
          </div>

          {/* System Status / Recent Activity Placeholder */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">System Status</h2>
            <div className="space-y-4">
              <StatusItem label="API Gateway" status="Operational" color="green" />
              <StatusItem label="Forensic Engine" status="Idle" color="blue" />
              <StatusItem label="Database" status="Connected" color="green" />
              <StatusItem label="Storage" status="Healthy" color="green" />
            </div>
            
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h3 className="font-bold text-gray-700 mb-2">Need Help?</h3>
              <p className="text-sm text-gray-500">
                Contact technical support at <a href="mailto:support@safechild.tech" className="text-blue-600">support@safechild.tech</a> for issues with forensic extraction or server maintenance.
              </p>
            </div>
          </div>

        </div>
      </main>
      
      <Footer />
    </div>
  );
};

// Sub-components for cleaner code
const StatCard = ({ title, value, icon, color, link }) => {
  const colorClasses = {
    blue: "text-blue-600 bg-blue-50",
    green: "text-green-600 bg-green-50",
    yellow: "text-yellow-600 bg-yellow-50",
    purple: "text-purple-600 bg-purple-50",
  };

  return (
    <Link to={link} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-500 text-sm font-medium uppercase tracking-wide">{title}</p>
          <h3 className="text-3xl font-bold text-gray-800 mt-2">{value}</h3>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </Link>
  );
};

const StatusItem = ({ label, status, color }) => {
  const dotColor = {
    green: "bg-green-500",
    blue: "bg-blue-500",
    yellow: "bg-yellow-500",
    red: "bg-red-500",
  };

  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-50 last:border-0">
      <span className="text-gray-600">{label}</span>
      <div className="flex items-center">
        <span className={`h-2.5 w-2.5 rounded-full ${dotColor[color]} mr-2`}></span>
        <span className="text-sm font-medium text-gray-800">{status}</span>
      </div>
    </div>
  );
};

export default AdminDashboard;
