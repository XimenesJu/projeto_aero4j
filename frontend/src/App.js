import React, { useState, useEffect } from 'react';
import '@/App.css';
import axios from 'axios';
import { Loader2, Send, Database, GitBranch, Sparkles, Code2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ForceGraph2D from 'react-force-graph-2d';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [examples, setExamples] = useState([]);
  const [dataSeeded, setDataSeeded] = useState(false);
  const [activeTab, setActiveTab] = useState('query');

  useEffect(() => {
    loadExamples();
    loadGraphData();
  }, []);

  const loadExamples = async () => {
    try {
      const res = await axios.get(`${API}/examples`);
      setExamples(res.data);
    } catch (error) {
      console.error('Error loading examples:', error);
    }
  };

  const loadGraphData = async () => {
    try {
      const res = await axios.get(`${API}/graph/data`);
      setGraphData(res.data);
    } catch (error) {
      console.error('Error loading graph data:', error);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await axios.post(`${API}/graphrag/query`, { query });
      setResponse(res.data);
      toast.success('Consulta executada com sucesso!');
      // Refresh graph data after query
      loadGraphData();
    } catch (error) {
      console.error('Error executing query:', error);
      toast.error('Erro ao executar consulta: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSeedData = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/seed-data`, { clear_existing: true });
      toast.success(`Dados populados: ${res.data.airports} aeroportos, ${res.data.airlines} companhias, ${res.data.routes} rotas`);
      setDataSeeded(true);
      loadGraphData();
    } catch (error) {
      console.error('Error seeding data:', error);
      toast.error('Erro ao popular dados: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-slate-200 dots-pattern">
      {/* Header */}
      <header className="border-b border-[#27272a] bg-[#18181b]/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <GitBranch className="h-8 w-8 text-cyan-400" />
              <div>
                <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
                  AeroGraph <span className="text-cyan-400">Analytics</span>
                </h1>
                <p className="text-sm text-slate-400">Análise de Redes de Aviação com GraphRAG + Neo4j</p>
              </div>
            </div>
            <Button
              onClick={handleSeedData}
              disabled={loading || dataSeeded}
              className="bg-cyan-400 text-black hover:bg-cyan-500 font-semibold rounded-md transition-all shadow-[0_0_15px_-3px_rgba(34,211,238,0.4)]"
              data-testid="seed-data-button"
            >
              <Database className="mr-2 h-4 w-4" />
              {dataSeeded ? 'Dados Carregados' : 'Popular Dados de Exemplo'}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-[#18181b] border border-[#27272a] mb-6" data-testid="tabs-list">
            <TabsTrigger value="query" className="data-[state=active]:bg-cyan-950/30 data-[state=active]:text-cyan-400" data-testid="query-tab">
              <Sparkles className="mr-2 h-4 w-4" />
              GraphRAG Query
            </TabsTrigger>
            <TabsTrigger value="graph" className="data-[state=active]:bg-cyan-950/30 data-[state=active]:text-cyan-400" data-testid="graph-tab">
              <GitBranch className="mr-2 h-4 w-4" />
              Visualização do Grafo
            </TabsTrigger>
            <TabsTrigger value="examples" className="data-[state=active]:bg-cyan-950/30 data-[state=active]:text-cyan-400" data-testid="examples-tab">
              <Code2 className="mr-2 h-4 w-4" />
              Exemplos
            </TabsTrigger>
          </TabsList>

          {/* Query Tab */}
          <TabsContent value="query" className="space-y-6" data-testid="query-content">
            <Card className="bg-[#18181b] border-[#27272a] p-6">
              <h2 className="text-xl font-semibold mb-4 text-cyan-400" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Faça sua Pergunta em Linguagem Natural
              </h2>
              <div className="flex space-x-2">
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                  placeholder="Ex: Quais aeroportos estão no Brasil?"
                  className="bg-[#09090b] border-white/10 focus:border-cyan-500/50 focus:ring-cyan-500/20 text-slate-200 placeholder:text-slate-600 flex-1"
                  disabled={loading}
                  data-testid="query-input"
                />
                <Button
                  onClick={handleQuery}
                  disabled={loading || !query.trim()}
                  className="bg-cyan-400 text-black hover:bg-cyan-500 font-semibold rounded-md transition-all"
                  data-testid="submit-query-button"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </Card>

            {response && (
              <div className="space-y-4" data-testid="query-response">
                <Card className="bg-[#18181b] border-[#27272a] p-6 message-bubble">
                  <h3 className="text-lg font-semibold mb-2 text-amber-500">Resposta</h3>
                  <p className="text-slate-300 leading-relaxed" data-testid="response-answer">{response.answer}</p>
                </Card>

                <Card className="bg-[#18181b] border-[#27272a] p-6 message-bubble">
                  <h3 className="text-lg font-semibold mb-3 text-cyan-400 flex items-center">
                    <Code2 className="mr-2 h-5 w-5" />
                    Query Cypher Gerada
                  </h3>
                  <div className="cypher-display" data-testid="cypher-query">
                    <code>{response.cypher_query}</code>
                  </div>
                </Card>

                {response.results && response.results.length > 0 && (
                  <Card className="bg-[#18181b] border-[#27272a] p-6 message-bubble">
                    <h3 className="text-lg font-semibold mb-3 text-amber-500">Resultados ({response.results.length})</h3>
                    <div className="overflow-x-auto" data-testid="query-results">
                      <pre className="text-sm text-slate-400" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                        {JSON.stringify(response.results.slice(0, 10), null, 2)}
                      </pre>
                    </div>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          {/* Graph Tab */}
          <TabsContent value="graph" data-testid="graph-content">
            <Card className="bg-[#18181b] border-[#27272a] p-6">
              <h2 className="text-xl font-semibold mb-4 text-cyan-400" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Rede de Aviação - Grafo Interativo
              </h2>
              <div className="network-graph-container" style={{ height: '600px' }} data-testid="graph-visualization">
                {graphData.nodes.length > 0 ? (
                  <ForceGraph2D
                    graphData={graphData}
                    nodeLabel="name"
                    nodeAutoColorBy="label"
                    nodeRelSize={6}
                    linkDirectionalArrowLength={3.5}
                    linkDirectionalArrowRelPos={1}
                    linkColor={() => 'rgba(34, 211, 238, 0.4)'}
                    nodeCanvasObject={(node, ctx, globalScale) => {
                      const label = node.name;
                      const fontSize = 12 / globalScale;
                      ctx.font = `${fontSize}px JetBrains Mono`;
                      const textWidth = ctx.measureText(label).width;
                      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.4);

                      // Node circle
                      ctx.fillStyle = node.label === 'Airport' ? '#22d3ee' : '#f59e0b';
                      ctx.beginPath();
                      ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                      ctx.fill();

                      // Label background
                      ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
                      ctx.fillRect(
                        node.x - bckgDimensions[0] / 2,
                        node.y + 8,
                        bckgDimensions[0],
                        bckgDimensions[1]
                      );

                      // Label text
                      ctx.textAlign = 'center';
                      ctx.textBaseline = 'middle';
                      ctx.fillStyle = node.label === 'Airport' ? '#22d3ee' : '#f59e0b';
                      ctx.fillText(label, node.x, node.y + 8 + bckgDimensions[1] / 2);
                    }}
                    backgroundColor="#09090b"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-slate-400">Carregue os dados de exemplo para visualizar o grafo</p>
                  </div>
                )}
              </div>
            </Card>
          </TabsContent>

          {/* Examples Tab */}
          <TabsContent value="examples" data-testid="examples-content">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {examples.map((example) => (
                <Card
                  key={example.id}
                  className="bg-[#18181b] border-[#27272a] p-6 hover:border-cyan-500/30 transition-all cursor-pointer group"
                  onClick={() => {
                    handleExampleClick(example.question);
                    setActiveTab('query');
                  }}
                  data-testid={`example-card-${example.id}`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center text-cyan-400 font-semibold group-hover:bg-cyan-400/20">
                      {example.id}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-200 mb-1 group-hover:text-cyan-400 transition-colors">
                        {example.question}
                      </h3>
                      <p className="text-sm text-slate-400">{example.description}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#27272a] mt-12 py-6 text-center text-sm text-slate-500">
        <p>AeroGraph Analytics - Demonstração de GraphRAG com Neo4j, LangChain e Gemini 2.5 Flash</p>
      </footer>
    </div>
  );
};

export default App;