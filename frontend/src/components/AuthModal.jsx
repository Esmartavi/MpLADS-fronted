import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Lock, 
  User, 
  Building2, 
  MapPin, 
  Landmark, 
  Vote, 
  X, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  Search,
  Mail,
  HelpCircle
} from 'lucide-react';
import { api } from '../services/api';

export default function AuthModal({ isOpen, onClose, initialMode = 'login', onAuthSuccess, activeRole }) {
  const [mode, setMode] = useState(initialMode); // 'login' | 'signup'
  const [selectedRole, setSelectedRole] = useState('ministry');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  // Dynamic Options from dataset
  const [authOptions, setAuthOptions] = useState({
    states: [],
    districts_by_state: {},
    mps: []
  });

  // Login form state
  const [loginForm, setLoginForm] = useState({
    username: '',
    password: ''
  });

  // Sign up form state
  const [signupForm, setSignupForm] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    name: '',
    email: '',
    designation: '',
    state: '',
    ida: '',
    mp_name: '',
    house: '',
    clearance_code: ''
  });

  // MP filters
  const [mpSearch, setMpSearch] = useState('');
  const [loginMpSearch, setLoginMpSearch] = useState('');
  const [loginMpState, setLoginMpState] = useState('');
  const [loginSelectedMp, setLoginSelectedMp] = useState('');

  useEffect(() => {
    setMode(initialMode);
    setError(null);
  }, [initialMode, isOpen]);

  // Load dynamic states, districts, and all 774+ MPs
  useEffect(() => {
    if (isOpen) {
      api.getAuthOptions().then(opts => {
        setAuthOptions(opts);
        if (opts.states && opts.states.length > 0 && !signupForm.state) {
          const defaultState = opts.states.includes('Uttar Pradesh') ? 'Uttar Pradesh' : opts.states[0];
          setSignupForm(prev => ({
            ...prev,
            state: defaultState,
            ida: (opts.districts_by_state[defaultState] || [])[0] || ''
          }));
        }
      }).catch(err => console.error('Failed to load auth options', err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  // Available districts for the currently chosen state
  const currentDistricts = (authOptions.districts_by_state && signupForm.state)
    ? (authOptions.districts_by_state[signupForm.state] || [])
    : [];

  // Filtered MPs for Signup
  const filteredMps = (authOptions.mps || []).filter(m => {
    const matchState = !signupForm.state || m.state.toLowerCase() === signupForm.state.toLowerCase();
    const matchHouse = !signupForm.house || m.house.toLowerCase() === signupForm.house.toLowerCase();
    const matchQuery = !mpSearch || m.name.toLowerCase().includes(mpSearch.toLowerCase()) || (m.constituency && m.constituency.toLowerCase().includes(mpSearch.toLowerCase()));
    return matchState && matchHouse && matchQuery;
  });

  // Filtered MPs for Login MP Directory
  const filteredLoginMps = (authOptions.mps || []).filter(m => {
    const matchState = !loginMpState || m.state.toLowerCase() === loginMpState.toLowerCase();
    const matchQuery = !loginMpSearch || m.name.toLowerCase().includes(loginMpSearch.toLowerCase()) || (m.constituency && m.constituency.toLowerCase().includes(loginMpSearch.toLowerCase()));
    return matchState && matchQuery;
  });

  const handleStateChange = (newState) => {
    const districts = authOptions.districts_by_state[newState] || [];
    setSignupForm(prev => ({
      ...prev,
      state: newState,
      ida: districts[0] || ''
    }));
  };

  // Sign In submit
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!loginForm.username.trim() || !loginForm.password) {
      setError('Please enter your official username, email, or MP name along with your password.');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const user = await api.login(loginForm.username.trim(), loginForm.password);
      if (onAuthSuccess) onAuthSuccess(user);
      onClose();
    } catch (err) {
      setError(err.message || 'Invalid official credentials. Please verify and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Sign Up submit with strict validation
  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!signupForm.name.trim()) {
      setError('Official full name is required');
      return;
    }
    if (!signupForm.username.trim() || signupForm.username.trim().length < 3) {
      setError('Username must be at least 3 characters long');
      return;
    }

    // Mandatory Email Check
    const cleanEmail = signupForm.email.trim();
    if (!cleanEmail) {
      setError('Official email address is mandatory for registration');
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(cleanEmail)) {
      setError('Please enter a valid official email address (e.g. official@mospi.gov.in or official@nic.in)');
      return;
    }

    // Password Complexity: >=8 chars, at least 1 letter, 1 number, 1 special character
    const pwd = signupForm.password;
    if (pwd.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    if (!/[A-Za-z]/.test(pwd)) {
      setError('Password must contain at least one letter');
      return;
    }
    if (!/\d/.test(pwd)) {
      setError('Password must contain at least one number');
      return;
    }
    if (!/[^A-Za-z0-9]/.test(pwd)) {
      setError('Password must contain at least one special character (e.g. @, #, $, %, !, &, *)');
      return;
    }

    if (pwd !== signupForm.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Role-specific checks
    if (selectedRole === 'state' && !signupForm.state) {
      setError('Please select your designated State / Union Territory jurisdiction');
      return;
    }
    if (selectedRole === 'district' && (!signupForm.state || !signupForm.ida)) {
      setError('Please select both State and Implementing District Authority (IDA)');
      return;
    }
    if (selectedRole === 'mp' && !signupForm.mp_name) {
      setError('Please select your Member of Parliament designation from the official directory');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        username: signupForm.username.trim().toLowerCase(),
        password: signupForm.password,
        role: selectedRole,
        name: signupForm.name.trim(),
        email: cleanEmail.toLowerCase(),
        designation: signupForm.designation.trim() || undefined,
        state: selectedRole !== 'ministry' ? signupForm.state : undefined,
        ida: selectedRole === 'district' ? signupForm.ida : undefined,
        mp_name: selectedRole === 'mp' ? signupForm.mp_name : undefined,
        clearance_code: signupForm.clearance_code || undefined,
      };

      const user = await api.register(payload);
      if (onAuthSuccess) onAuthSuccess(user);
      onClose();
    } catch (err) {
      setError(err.message || 'Registration failed. Please check form values.');
    } finally {
      setLoading(false);
    }
  };

  const roleTypes = [
    {
      id: 'ministry',
      title: 'MoSPI Ministry Official',
      badge: 'National Directorate',
      desc: 'Central Vigilance, policy enforcement & pan-India statutory oversight (All 36 States/UTs)',
      icon: Landmark,
      color: 'from-violet-500/20 to-purple-600/10 border-violet-500/30 text-violet-400'
    },
    {
      id: 'state',
      title: 'State Nodal Authority',
      badge: 'State Nodal Jurisdiction',
      desc: 'State-level oversight, milestone releases & district fund compliance tracking',
      icon: Building2,
      color: 'from-cyan-500/20 to-sky-600/10 border-cyan-500/30 text-cyan-400'
    },
    {
      id: 'district',
      title: 'District Authority',
      badge: 'District Magistrate / IDA',
      desc: 'Ground execution, contractor sanctions & physical photo verification audits',
      icon: MapPin,
      color: 'from-emerald-500/20 to-teal-600/10 border-emerald-500/30 text-emerald-400'
    },
    {
      id: 'mp',
      title: 'Member of Parliament',
      badge: 'Constituency Level',
      desc: 'Lok Sabha & Rajya Sabha parliamentary fund audit, sanctions & vendor watch',
      icon: Vote,
      color: 'from-amber-500/20 to-yellow-600/10 border-amber-500/30 text-amber-400'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-2xl max-h-[92vh] overflow-y-auto rounded-2xl bg-slate-900 border border-slate-700/80 shadow-2xl text-slate-100 flex flex-col no-scrollbar"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Header Ribbon */}
        <div className="sticky top-0 z-20 flex items-center justify-between px-6 py-4 bg-slate-900/95 border-b border-slate-800 backdrop-blur-md">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-sky-600/10 border border-cyan-500/30 text-cyan-400 shadow-glow-cyan">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
                भारत सरकार // MoSPI National Vigilance Portal
              </div>
              <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                BHARAT-DRISHTI Access Control
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex border-b border-slate-800 px-6 pt-4 bg-slate-900">
          <button
            type="button"
            onClick={() => { setMode('login'); setError(null); }}
            className={`pb-3 text-sm font-semibold border-b-2 mr-6 transition-all ${
              mode === 'login'
                ? 'border-cyan-400 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In to Account
          </button>
          <button
            type="button"
            onClick={() => { setMode('signup'); setError(null); }}
            className={`pb-3 text-sm font-semibold border-b-2 transition-all ${
              mode === 'signup'
                ? 'border-cyan-400 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Register New Government Official
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mx-6 mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <div className="p-6">
          {mode === 'login' ? (
            /* ─────────────────────────────────────────────────────────────
               SIGN IN FORM
            ───────────────────────────────────────────────────────────── */
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                  Official Username, Email or Member of Parliament
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={loginForm.username}
                    onChange={(e) => {
                      setLoginForm({ ...loginForm, username: e.target.value });
                      if (error) setError(null);
                    }}
                    placeholder="Enter registered username, email, or MP name"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={loginForm.password}
                    onChange={(e) => {
                      setLoginForm({ ...loginForm, password: e.target.value });
                      if (error) setError(null);
                    }}
                    placeholder="Enter account password"
                    className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* MP Directory Lookup Helper on Login Tab */}
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-amber-400 flex items-center gap-1.5">
                    <Vote className="w-3.5 h-3.5" />
                    Member of Parliament Directory (774 Official MPs)
                  </span>
                  <span className="text-[10px] text-slate-500">Fast MP Selection</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <select
                    value={loginMpState}
                    onChange={(e) => setLoginMpState(e.target.value)}
                    className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white text-xs"
                  >
                    <option value="">-- All States & UTs ({authOptions.mps.length} MPs) --</option>
                    {authOptions.states.map(st => {
                      const count = (authOptions.mps || []).filter(m => m.state.toLowerCase() === st.toLowerCase()).length;
                      return (
                        <option key={st} value={st}>{st} ({count} MPs)</option>
                      );
                    })}
                  </select>
                  <div className="relative">
                    <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500" />
                    <input
                      type="text"
                      value={loginMpSearch}
                      onChange={(e) => setLoginMpSearch(e.target.value)}
                      placeholder="Search MP name..."
                      className="w-full pl-7 pr-2 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white text-xs"
                    />
                  </div>
                </div>
                <select
                  value={loginSelectedMp}
                  onChange={(e) => {
                    const chosen = e.target.value;
                    setLoginSelectedMp(chosen);
                    if (chosen) {
                      setLoginForm(prev => ({ ...prev, username: chosen }));
                      if (error) setError(null);
                    }
                  }}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 text-xs focus:outline-none focus:border-amber-500"
                >
                  <option value="">-- Select Member of Parliament from Directory ({filteredLoginMps.length} Available) --</option>
                  {filteredLoginMps.map(m => (
                    <option key={m.name} value={m.name}>
                      {m.name} — {m.constituency ? `${m.constituency}, ` : ''}{m.state} ({m.house})
                    </option>
                  ))}
                </select>
                <p className="text-[10px] text-slate-500">
                  Selecting an MP automatically fills your username field above.
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-sky-600 hover:from-cyan-500 hover:to-sky-500 text-white font-semibold text-sm transition-all shadow-glow-cyan active:scale-[0.99] flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <span>Authenticating Official...</span>
                ) : (
                  <>
                    <span>Authenticate & Access Portal</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="pt-2 text-center text-xs text-slate-500">
                Don't have an official account?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('signup'); setError(null); }}
                  className="text-cyan-400 hover:underline font-semibold"
                >
                  Register New Official
                </button>
              </div>
            </form>
          ) : (
            /* ─────────────────────────────────────────────────────────────
               SIGN UP FORM (4 Government Tiers)
            ───────────────────────────────────────────────────────────── */
            <form onSubmit={handleSignupSubmit} className="space-y-4">
              
              {/* Step 1: User Role Selection */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Select Government Official Tier
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {roleTypes.map(rt => {
                    const Icon = rt.icon;
                    const isSelected = selectedRole === rt.id;
                    return (
                      <button
                        key={rt.id}
                        type="button"
                        onClick={() => setSelectedRole(rt.id)}
                        className={`p-3 rounded-xl text-left border transition-all flex items-start space-x-3 ${
                          isSelected
                            ? 'bg-slate-800/90 border-cyan-400 ring-1 ring-cyan-400/50 shadow-sm'
                            : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40'
                        }`}
                      >
                        <div className={`p-2 rounded-lg border ${rt.color}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-xs text-white">{rt.title}</span>
                            {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />}
                          </div>
                          <div className="text-[10px] text-cyan-400/80 font-mono">{rt.badge}</div>
                          <div className="text-[10px] text-slate-400 mt-0.5 line-clamp-2 leading-tight">
                            {rt.desc}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Step 2: Role-Specific Dropdowns & Jurisdiction (Hidden for Pan-India Ministry Official) */}
              {selectedRole !== 'ministry' && (
                <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3">
                  <div className="text-[11px] font-mono uppercase tracking-wider text-cyan-400 font-semibold flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5" />
                    Jurisdiction & Official Assignment
                  </div>

                  {/* State Nodal & District Authority: State Select */}
                  {(selectedRole === 'state' || selectedRole === 'district') && (
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Designated State / Union Territory ({authOptions.states.length} States & UTs Available) <span className="text-rose-400">*</span>
                      </label>
                      <select
                        value={signupForm.state}
                        onChange={(e) => handleStateChange(e.target.value)}
                        className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                      >
                        <option value="">-- Choose State / UT ({authOptions.states.length} Available) --</option>
                        {authOptions.states.map(st => {
                          const dCount = (authOptions.districts_by_state[st] || []).length;
                          return (
                            <option key={st} value={st}>
                              {st} ({dCount} Districts)
                            </option>
                          );
                        })}
                      </select>
                    </div>
                  )}

                  {/* District Authority: IDA District Select */}
                  {selectedRole === 'district' && (
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Implementing District Authority (IDA - {currentDistricts.length} Official Districts) <span className="text-rose-400">*</span>
                      </label>
                      <select
                        value={signupForm.ida}
                        onChange={(e) => setSignupForm({ ...signupForm, ida: e.target.value })}
                        className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                      >
                        <option value="">-- Choose Implementing District Authority ({currentDistricts.length} Available) --</option>
                        {currentDistricts.map(dist => (
                          <option key={dist} value={dist}>{dist}</option>
                        ))}
                      </select>
                      <p className="text-[10px] text-cyan-400 font-mono mt-1">
                        Showing all {currentDistricts.length} official implementing districts in {signupForm.state || 'selected state'}.
                      </p>
                    </div>
                  )}

                  {/* Member of Parliament (MP): House + State + Search + Member Selector */}
                  {selectedRole === 'mp' && (
                    <div className="space-y-2.5">
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div>
                          <label className="block text-xs font-semibold text-slate-300 mb-1">
                            Filter by State / UT
                          </label>
                          <select
                            value={signupForm.state}
                            onChange={(e) => setSignupForm({ ...signupForm, state: e.target.value })}
                            className="w-full px-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs"
                          >
                            <option value="">-- All States & UTs (Pan-India) --</option>
                            {authOptions.states.map(st => {
                              const stateMps = (authOptions.mps || []).filter(m => {
                                const matchState = m.state.toLowerCase() === st.toLowerCase();
                                const matchHouse = !signupForm.house || m.house.toLowerCase() === signupForm.house.toLowerCase();
                                return matchState && matchHouse;
                              });
                              const houseLabel = signupForm.house === 'LS' ? 'Lok Sabha MPs' : signupForm.house === 'RS' ? 'Rajya Sabha MPs' : 'MPs';
                              return (
                                <option key={st} value={st}>
                                  {st} ({stateMps.length} {houseLabel})
                                </option>
                              );
                            })}
                          </select>
                        </div>

                        <div>
                          <label className="block text-xs font-semibold text-slate-300 mb-1">
                            Parliamentary House
                          </label>
                          <select
                            value={signupForm.house}
                            onChange={(e) => setSignupForm({ ...signupForm, house: e.target.value })}
                            className="w-full px-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs"
                          >
                            <option value="">All Houses (LS & RS)</option>
                            <option value="LS">Lok Sabha (House of the People)</option>
                            <option value="RS">Rajya Sabha (Council of States)</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-xs font-semibold text-slate-300 mb-1">
                            Search MP Name / Constituency
                          </label>
                          <div className="relative">
                            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
                            <input
                              type="text"
                              value={mpSearch}
                              onChange={(e) => setMpSearch(e.target.value)}
                              placeholder="Filter list..."
                              className="w-full pl-8 pr-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs"
                            />
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">
                          Select Member of Parliament <span className="text-rose-400">*</span>
                        </label>
                        <select
                          value={signupForm.mp_name}
                          onChange={(e) => {
                            const mName = e.target.value;
                            const mpObj = authOptions.mps.find(m => m.name === mName);
                            setSignupForm({
                              ...signupForm,
                              mp_name: mName,
                              name: mName,
                              state: mpObj && mpObj.state ? mpObj.state : signupForm.state
                            });
                          }}
                          className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                        >
                          <option value="">-- Choose Member of Parliament ({filteredMps.length} Available) --</option>
                          {filteredMps.map(m => (
                            <option key={m.name} value={m.name}>
                              {m.name} — {m.constituency ? `${m.constituency}, ` : ''}{m.state} ({m.house})
                            </option>
                          ))}
                        </select>
                        <p className="text-[10px] text-cyan-400/90 font-mono mt-1">
                          {signupForm.state
                            ? `Showing all ${filteredMps.length} MPs for ${signupForm.state}${signupForm.house ? ` (${signupForm.house === 'LS' ? 'Lok Sabha' : 'Rajya Sabha'})` : ''}.`
                            : `Showing all ${filteredMps.length} official Lok Sabha & Rajya Sabha MPs nationwide.`}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Step 3: Identity & Credentials */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Official Full Name <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={signupForm.name}
                    onChange={(e) => setSignupForm({ ...signupForm, name: e.target.value })}
                    placeholder="e.g. Dr. Arvind Sharma"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Username <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={signupForm.username}
                    onChange={(e) => setSignupForm({ ...signupForm, username: e.target.value })}
                    placeholder="e.g. arvind_sharma"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              {/* Mandatory Email */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
                  <span>Government / Official Email <span className="text-rose-400">*</span></span>
                  <span className="text-[10px] text-slate-400 font-mono">Mandatory</span>
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="email"
                    required
                    value={signupForm.email}
                    onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })}
                    placeholder="e.g. official.name@mospi.gov.in or @nic.in"
                    className="w-full pl-10 pr-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              {/* Password & Confirm Password */}
              <div className="space-y-1.5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Password <span className="text-rose-400">*</span>
                    </label>
                    <input
                      type="password"
                      required
                      value={signupForm.password}
                      onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })}
                      placeholder="Min 8 chars, letter, number, symbol"
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Confirm Password <span className="text-rose-400">*</span>
                    </label>
                    <input
                      type="password"
                      required
                      value={signupForm.confirmPassword}
                      onChange={(e) => setSignupForm({ ...signupForm, confirmPassword: e.target.value })}
                      placeholder="Re-enter password"
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>
                <div className="text-[10px] text-slate-400 flex items-center gap-1.5 pl-1">
                  <HelpCircle className="w-3 h-3 text-cyan-400 flex-shrink-0" />
                  <span>Password policy: Minimum 8 characters, at least one letter, one number, and one special character.</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-3 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-sky-600 hover:from-cyan-500 hover:to-sky-500 text-white font-semibold text-sm transition-all shadow-glow-cyan active:scale-[0.99] flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <span>Registering Official Account...</span>
                ) : (
                  <>
                    <span>Register & Access Vigilance System</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="pt-2 text-center text-xs text-slate-500">
                Already registered?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('login'); setError(null); }}
                  className="text-cyan-400 hover:underline font-semibold"
                >
                  Sign In Instead
                </button>
              </div>

            </form>
          )}
        </div>

      </div>
    </div>
  );
}
