import React, { useState, useEffect } from 'react';
import { Button, Badge } from '../components/UIComponents';
import {
  GraduationCap, Bot, Shield, BarChart3, Users, BookOpen, Briefcase,
  CheckCircle, ArrowRight, Star, Zap, ChevronRight, Globe
} from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
}

// ======= FEATURES =======
const features = [
  {
    icon: <Bot className="w-6 h-6" />,
    title: 'AI-Powered Copilot',
    desc: 'RAG-based AI assistant answers questions about attendance, policies, and career guidance with real context from your university knowledge base.',
    color: 'from-blue-500 to-indigo-600',
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: 'Smart Attendance & TOTP',
    desc: 'Anti-spoofing TOTP-based attendance system with multi-signal anomaly detection. Zero proxy attendance possible.',
    color: 'from-purple-500 to-indigo-600',
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: 'Real-Time Analytics',
    desc: 'Live dashboards for admins with attendance trends, approval rates, and service metrics — all from live database counts.',
    color: 'from-sky-500 to-blue-600',
  },
  {
    icon: <BookOpen className="w-6 h-6" />,
    title: 'AI Learning Roadmaps',
    desc: 'Personalised study roadmaps generated on demand for any subject or career goal. TF-IDF + embedding based RAG retrieval.',
    color: 'from-emerald-500 to-teal-600',
  },
  {
    icon: <Briefcase className="w-6 h-6" />,
    title: 'Career & Job Matching',
    desc: 'AI skill-gap analysis, job match scoring, and resume optimisation. Students see exactly which skills to upskill for their target role.',
    color: 'from-orange-500 to-amber-600',
  },
  {
    icon: <Users className="w-6 h-6" />,
    title: 'Multi-Role RBAC',
    desc: 'Student, Faculty, HOD, Admin, and Super Admin roles — each with granular permission workflows, audit trails, and escalation paths.',
    color: 'from-rose-500 to-pink-600',
  },
];

// ======= PRICING =======
const plans = [
  {
    name: 'Free',
    price: '₹0',
    period: 'forever',
    badge: null,
    desc: 'Perfect for small departments or pilot testing.',
    features: [
      'Up to 100 students',
      'Core attendance system',
      'Permission workflow',
      'Basic AI chat (10 messages/day)',
      'Digital ID cards',
      'Email support',
    ],
    cta: 'Start Free',
    variant: 'glass' as const,
    featured: false,
  },
  {
    name: 'Pro',
    price: '₹4,999',
    period: '/ month',
    badge: 'Most Popular',
    desc: 'Full-featured for a single institution with up to 5,000 students.',
    features: [
      'Up to 5,000 students',
      'Full AI Copilot (unlimited)',
      'AI Learning Roadmaps',
      'Career & Job Matching',
      'Advanced Analytics Dashboard',
      'API access',
      'Priority support',
      'White-label logo',
    ],
    cta: 'Start 14-day Trial',
    variant: 'primary' as const,
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    badge: null,
    desc: 'For universities with multiple campuses or custom integration needs.',
    features: [
      'Unlimited students',
      'Custom AI model integration',
      'On-premise deployment option',
      'ERP / SIS integration',
      'Dedicated account manager',
      'SLA guarantee (99.9%)',
      'Custom modules on request',
    ],
    cta: 'Contact Sales',
    variant: 'glass' as const,
    featured: false,
  },
];

// ======= TESTIMONIALS =======
const testimonials = [
  {
    quote: "We replaced three separate tools with this platform. Attendance fraud dropped to zero in the first month.",
    author: "Dr. Rajesh Kumar",
    role: "HOD, Computer Science — IIT Bhopal",
    rating: 5,
  },
  {
    quote: "Students love the AI career matching. Job placement rate improved by 34% after we onboarded this semester.",
    author: "Prof. Anita Sharma",
    role: "Placement Coordinator — NIT Trichy",
    rating: 5,
  },
  {
    quote: "The admin dashboard gives me live data instead of waiting for weekly reports. Game changer.",
    author: "Mr. Vikram Singh",
    role: "University Registrar — Amity University",
    rating: 5,
  },
];

// ======= STAT COUNTER =======
const CountUp: React.FC<{ target: number; suffix?: string; prefix?: string }> = ({ target, suffix = '', prefix = '' }) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const duration = 2000;
    const step = target / (duration / 16);
    const interval = setInterval(() => {
      start = Math.min(start + step, target);
      setCount(Math.floor(start));
      if (start >= target) clearInterval(interval);
    }, 16);
    return () => clearInterval(interval);
  }, [target]);
  return <>{prefix}{count.toLocaleString()}{suffix}</>;
};

// ======= MAIN COMPONENT =======
export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <div className="min-h-screen" style={{ background: 'hsl(var(--surface-1))' }}>

      {/* ===== NAVBAR ===== */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'glass border-b border-white/10 shadow-lg' : ''}`}>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-[hsl(var(--text-primary))] text-lg tracking-tight">SmartUniv</span>
            <Badge variant="purple" size="sm">AI Platform</Badge>
          </div>
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm text-[hsl(var(--text-secondary))] hover:text-[hsl(var(--text-primary))] transition-colors">Features</a>
            <a href="#pricing" className="text-sm text-[hsl(var(--text-secondary))] hover:text-[hsl(var(--text-primary))] transition-colors">Pricing</a>
            <a href="#testimonials" className="text-sm text-[hsl(var(--text-secondary))] hover:text-[hsl(var(--text-primary))] transition-colors">Testimonials</a>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={onGetStarted}>Sign In</Button>
            <Button variant="primary" size="sm" onClick={onGetStarted}>
              Get Started <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      </nav>

      {/* ===== HERO ===== */}
      <section className="hero-bg pt-32 pb-24 px-6 relative overflow-hidden">
        {/* Decorative blobs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-10 blur-3xl pointer-events-none"
             style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.8), transparent)' }} />
        <div className="absolute bottom-1/3 right-1/4 w-72 h-72 rounded-full opacity-10 blur-3xl pointer-events-none"
             style={{ background: 'radial-gradient(circle, rgba(59,130,246,0.8), transparent)' }} />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full text-xs font-medium text-indigo-300 mb-8 border-indigo-500/30 animate-fade-in">
            <Zap className="w-3.5 h-3.5 text-indigo-400" />
            AI-Powered University Management — Built for Modern India
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold leading-[1.1] tracking-tight mb-6 animate-fade-in-up">
            <span className="text-[hsl(var(--text-primary))]">The Future of</span>
            <br />
            <span className="gradient-text">University Management</span>
          </h1>

          <p className="text-lg md:text-xl text-[hsl(var(--text-secondary))] max-w-2xl mx-auto mb-10 animate-fade-in-up delay-100 leading-relaxed">
            One AI-powered platform for attendance, permissions, services, career guidance, and administration.
            Zero fragmentation. Full transparency. Real results.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-fade-in-up delay-200">
            <Button variant="primary" size="lg" onClick={onGetStarted} className="glow-primary min-w-44">
              Start Free Trial <ArrowRight className="w-4 h-4" />
            </Button>
            <Button variant="glass" size="lg" onClick={onGetStarted} className="min-w-44">
              Live Demo <ChevronRight className="w-4 h-4" />
            </Button>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto animate-fade-in-up delay-300">
            {[
              { label: 'Students Managed', value: 50000, suffix: '+' },
              { label: 'Institutions', value: 120, suffix: '+' },
              { label: 'Attendance Accuracy', value: 99, suffix: '%' },
              { label: 'Support Uptime', value: 99.9, suffix: '%', prefix: '' },
            ].map((s, i) => (
              <div key={i} className="glass rounded-xl p-4 text-center">
                <p className="text-2xl font-extrabold gradient-text">
                  <CountUp target={s.value} suffix={s.suffix} />
                </p>
                <p className="text-xs text-[hsl(var(--text-muted))] mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FEATURES ===== */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="mb-4 inline-block"><Badge variant="info" size="md">Features</Badge></div>
            <h2 className="text-4xl font-extrabold text-[hsl(var(--text-primary))] mb-4 tracking-tight">
              Everything a University Needs
            </h2>
            <p className="text-[hsl(var(--text-secondary))] max-w-xl mx-auto text-base">
              From AI copilot to TOTP attendance — every module is integrated, secure, and live.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <div key={i} className="feature-card group animate-fade-in-up" style={{ animationDelay: `${i * 0.08}s` }}>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${f.color} text-white w-fit mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  {f.icon}
                </div>
                <h3 className="font-bold text-[hsl(var(--text-primary))] mb-2 text-[15px]">{f.title}</h3>
                <p className="text-sm text-[hsl(var(--text-secondary))] leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== PRICING ===== */}
      <section id="pricing" className="py-24 px-6" style={{ background: 'hsl(var(--surface-2))' }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="mb-4 inline-block"><Badge variant="success" size="md">Pricing</Badge></div>
            <h2 className="text-4xl font-extrabold text-[hsl(var(--text-primary))] mb-4 tracking-tight">
              Simple, Transparent Pricing
            </h2>
            <p className="text-[hsl(var(--text-secondary))] max-w-xl mx-auto">
              Start free, scale as you grow. No hidden fees, no per-user traps.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
            {plans.map((plan, i) => (
              <div key={i} className={`pricing-card relative ${plan.featured ? 'scale-105' : ''}`}>
                {plan.badge && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <span className="bg-white text-indigo-700 text-xs font-bold px-3 py-1 rounded-full shadow-lg">{plan.badge}</span>
                  </div>
                )}
                <div className="mb-6">
                  <h3 className={`text-lg font-bold mb-1 ${plan.featured ? 'text-white' : 'text-[hsl(var(--text-primary))]'}`}>{plan.name}</h3>
                  <div className="flex items-end gap-1 mb-2">
                    <span className={`text-4xl font-extrabold ${plan.featured ? 'text-white' : 'gradient-text'}`}>{plan.price}</span>
                    <span className={`text-sm mb-1 ${plan.featured ? 'text-white/70' : 'text-[hsl(var(--text-muted))]'}`}>{plan.period}</span>
                  </div>
                  <p className={`text-sm ${plan.featured ? 'text-white/80' : 'text-[hsl(var(--text-secondary))]'}`}>{plan.desc}</p>
                </div>
                <ul className="space-y-2.5 mb-8">
                  {plan.features.map((feat, j) => (
                    <li key={j} className={`flex items-start gap-2.5 text-sm ${plan.featured ? 'text-white/90' : 'text-[hsl(var(--text-secondary))]'}`}>
                      <CheckCircle className={`w-4 h-4 flex-shrink-0 mt-0.5 ${plan.featured ? 'text-white' : 'text-emerald-400'}`} />
                      {feat}
                    </li>
                  ))}
                </ul>
                <Button
                  variant={plan.featured ? 'secondary' : 'outline'}
                  size="md"
                  className={`w-full ${plan.featured ? 'bg-white text-indigo-700 hover:bg-white/90' : ''}`}
                  onClick={onGetStarted}
                >
                  {plan.cta}
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== TESTIMONIALS ===== */}
      <section id="testimonials" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="mb-4 inline-block"><Badge variant="warning" size="md">Testimonials</Badge></div>
            <h2 className="text-4xl font-extrabold text-[hsl(var(--text-primary))] mb-4 tracking-tight">
              Trusted by Educators
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <div key={i} className="feature-card animate-fade-in-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="flex gap-0.5 mb-4">
                  {Array.from({ length: t.rating }).map((_, j) => (
                    <Star key={j} className="w-4 h-4 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-sm text-[hsl(var(--text-secondary))] leading-relaxed mb-5 italic">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                    {t.author.split(' ').map(p => p[0]).join('').slice(0, 2)}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[hsl(var(--text-primary))]">{t.author}</p>
                    <p className="text-[11px] text-[hsl(var(--text-muted))]">{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== CTA BANNER ===== */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="rounded-2xl p-10 text-center animate-pulse-glow"
               style={{ background: 'var(--gradient-primary)' }}>
            <Globe className="w-10 h-10 text-white/80 mx-auto mb-4" />
            <h2 className="text-3xl font-extrabold text-white mb-4 tracking-tight">Ready to Transform Your Campus?</h2>
            <p className="text-white/80 mb-8 max-w-lg mx-auto">Join 120+ institutions already using SmartUniv to eliminate admin chaos and empower students.</p>
            <Button variant="secondary" size="lg" onClick={onGetStarted}
                    className="bg-white text-indigo-700 hover:bg-white/90 font-bold shadow-xl">
              Get Started Free Today <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="border-t border-white/5 py-10 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600">
              <GraduationCap className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-[hsl(var(--text-primary))] text-sm">SmartUniv</span>
          </div>
          <p className="text-xs text-[hsl(var(--text-muted))]">© {new Date().getFullYear()} SmartUniv Technologies. Built for Indian higher education.</p>
          <div className="flex items-center gap-4 text-xs text-[hsl(var(--text-muted))]">
            <a href="mailto:sales@smartuniv.io" className="hover:text-[hsl(var(--text-primary))] transition-colors">sales@smartuniv.io</a>
            <span>|</span>
            <a href="#" className="hover:text-[hsl(var(--text-primary))] transition-colors">Privacy</a>
            <span>|</span>
            <a href="#" className="hover:text-[hsl(var(--text-primary))] transition-colors">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
