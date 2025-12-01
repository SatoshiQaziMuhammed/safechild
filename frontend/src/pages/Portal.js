import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { forensicService } from '../lib/api';
import Header from '../components/Header';
import Footer from '../components/Footer';

const Portal = () => {
  const { user, logout } = useAuth();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const result = await forensicService.getMyCases();
        setCases(result.cases || []);
      } catch (error) {
        console.error("Failed to fetch cases", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Client Portal</h1>
            <p className="text-gray-600">Welcome back, {user?.firstName}</p>
          </div>
          <Link 
            to="/forensic-analysis" 
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg shadow-md transition duration-200"
          >
            + New Forensic Analysis
          </Link>
        </div>

        {/* Dashboard Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-gray-500 text-sm font-medium uppercase">Total Cases</h3>
            <p className="text-3xl font-bold text-gray-800 mt-2">{cases.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
             <h3 className="text-gray-500 text-sm font-medium uppercase">Completed Reports</h3>
             <p className="text-3xl font-bold text-green-600 mt-2">
               {cases.filter(c => c.status === 'completed').length}
             </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
             <h3 className="text-gray-500 text-sm font-medium uppercase">Pending Actions</h3>
             <p className="text-3xl font-bold text-yellow-600 mt-2">
               {cases.filter(c => c.status === 'processing').length}
             </p>
          </div>
        </div>

        {/* Recent Cases List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-800">Your Forensic Cases</h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading cases...</div>
          ) : cases.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No cases found. Start a new analysis to begin.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
                  <tr>
                    <th className="px-6 py-3">Case ID</th>
                    <th className="px-6 py-3">Date</th>
                    <th className="px-6 py-3">File</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {cases.map((c) => (
                    <tr key={c.case_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-medium text-gray-900">{c.case_id}</td>
                      <td className="px-6 py-4 text-gray-500">
                        {new Date(c.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-gray-500">{c.file_name}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold
                          ${c.status === 'completed' ? 'bg-green-100 text-green-800' : 
                            c.status === 'failed' ? 'bg-red-100 text-red-800' : 
                            'bg-yellow-100 text-yellow-800'}`}>
                          {c.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {c.status === 'completed' && (
                          <Link 
                            to="/forensic-analysis" 
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            View Report
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Portal;
