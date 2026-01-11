// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ urls_crawled: 0, entities_in_graph: 0 });
  const [message, setMessage] = useState('');

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/stats`);
      setStats(response.data);
    } catch (error) {
      console.log('Initializing system...');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setMessage('');
    try {
      const response = await axios.post(`${API_BASE}/query`, {
        query,
        max_results: 10
      });
      
      if (response.data.results) {
        setResults(response.data.results);
      } else {
        setMessage('No results found. Try a different query.');
        setResults([]);
      }
    } catch (error) {
      setMessage('System is initializing. Please wait a moment...');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Header */}
      <header className="max-w-6xl mx-auto mb-8">
        <h1 className="text-3xl font-bold text-gray-900">🧠 Web Knowledge Platform</h1>
        <p className="text-gray-600 mt-2">AI-powered web intelligence for Indian businesses</p>
        
        {/* Stats */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-500">Websites Crawled</div>
            <div className="text-2xl font-bold text-blue-600">{stats.urls_crawled}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-500">Entities Found</div>
            <div className="text-2xl font-bold text-green-600">{stats.entities_in_graph}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-500">Status</div>
            <div className="text-lg font-semibold text-green-600">Active</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-500">Last Updated</div>
            <div className="text-lg">Just now</div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto">
        {/* Search Section */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Search Business Information</h2>
          
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., 'steel companies contact information'"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search Knowledge Base'}
            </button>
          </form>
          
          {message && (
            <div className="mt-4 p-3 bg-yellow-50 text-yellow-800 rounded-lg">
              {message}
            </div>
          )}
          
          <div className="mt-6">
            <h3 className="font-medium text-gray-700 mb-2">💡 Try these examples:</h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setQuery('steel companies contact')}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Steel Companies
              </button>
              <button
                onClick={() => setQuery('tech companies email')}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Tech Companies
              </button>
              <button
                onClick={() => setQuery('manufacturing phone')}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Manufacturing
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Found {results.length} compan{results.length === 1 ? 'y' : 'ies'}
            </h2>
            
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg hover:border-blue-300">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold text-blue-700">
                        {result.company_name}
                      </h3>
                      <p className="text-gray-600 text-sm">{result.domain}</p>
                      <div className="mt-2">
                        <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          Confidence: {(result.confidence * 100).toFixed(0)}%
                        </span>
                        <span className="ml-2 inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                          {result.url_count} pages
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Contact Info */}
                  {result.contacts && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <h4 className="font-medium text-gray-700 mb-2">Contact Information:</h4>
                      
                      {result.contacts.emails && result.contacts.emails.length > 0 && (
                        <div className="mb-3">
                          <div className="text-sm text-gray-600 mb-1">Email:</div>
                          {result.contacts.emails.map((email, i) => (
                            <a
                              key={i}
                              href={`mailto:${email}`}
                              className="block text-blue-600 hover:text-blue-800"
                            >
                              {email}
                            </a>
                          ))}
                        </div>
                      )}
                      
                      {result.contacts.phones && result.contacts.phones.length > 0 && (
                        <div>
                          <div className="text-sm text-gray-600 mb-1">Phone:</div>
                          {result.contacts.phones.map((phone, i) => (
                            <div key={i} className="text-green-700">
                              {phone}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Results Message */}
        {results.length === 0 && query && !loading && !message && (
          <div className="text-center py-8">
            <div className="text-5xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">No results found</h3>
            <p className="text-gray-600">Try different keywords or check back later</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto mt-12 pt-8 border-t border-gray-200 text-center text-gray-600 text-sm">
        <p>Web Knowledge Platform • Production Deployment</p>
        <p className="mt-1">Processing top Indian business websites</p>
        <p className="mt-2 text-xs text-gray-500">System updates every 2 hours</p>
      </footer>
    </div>
  );
}

export default App;