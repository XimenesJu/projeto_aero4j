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
  const [filteredGraphData, setFilteredGraphData] = useState({ nodes: [], links: [] });
  const [examples, setExamples] = useState([]);
  const [dataSeeded, setDataSeeded] = useState(false);
  const [activeTab, setActiveTab] = useState('query');
  
  // Graph filter states
  const [showAirports, setShowAirports] = useState(true);
  const [showAirlines, setShowAirlines] = useState(true);
  const [showRoutes, setShowRoutes] = useState(true);
  const [graphMode, setGraphMode] = useState('all'); // 'all', 'query-results', 'preset'
  const [currentDataset, setCurrentDataset] = useState('BR'); // 'full' or 'BR'

  useEffect(() => {
    loadExamples();
    // Load graph data without seeding
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
      applyGraphFilters(res.data);
    } catch (error) {
      console.error('Error loading graph data:', error);
    }
  };

  // Apply filters to graph data
  const applyGraphFilters = (data = graphData) => {
    // Se não há dados, retorna vazio
    if (!data || !data.nodes || !data.links) {
      setFilteredGraphData({ nodes: [], links: [] });
      return;
    }

    let filtered = { nodes: [], links: [] };

    // If showing query results, use only nodes from last query
    if (graphMode === 'query-results' && response?.results) {
      const queryNodeIds = new Set();
      response.results.forEach(result => {
        Object.values(result).forEach(value => {
          if (value?.code) queryNodeIds.add(value.code);
          if (value?.name) queryNodeIds.add(value.name);
        });
      });
      
      filtered.nodes = data.nodes.filter(node => 
        queryNodeIds.has(node.id) || queryNodeIds.has(node.name)
      );
    } else {
      filtered.nodes = [...data.nodes];
    }

    // Apply dataset filter (BR or full)
    if (currentDataset === 'BR') {
      filtered.nodes = filtered.nodes.filter(node => {
        // Keep Brazilian airports
        if (node.label === 'Airport' && node.country === 'BR') return true;
        // Keep airlines that operate in Brazil (connected to BR airports)
        if (node.label === 'Airline') {
          // Will check connections after filtering
          return true;
        }
        return false;
      });
      
      // Filter routes to only BR-to-BR connections
      const brAirportIds = new Set(
        filtered.nodes
          .filter(n => n.label === 'Airport' && n.country === 'BR')
          .map(n => n.id)
      );
      
      filtered.links = (data.links || []).filter(link => {
        const sourceId = link.source.id || link.source;
        const targetId = link.target.id || link.target;
        return brAirportIds.has(sourceId) && brAirportIds.has(targetId);
      });
      
      // Keep only airlines that have routes in the filtered data
      const airlinesInRoutes = new Set(filtered.links.map(l => l.airline).filter(Boolean));
      filtered.nodes = filtered.nodes.filter(node => {
        if (node.label === 'Airline') {
          return airlinesInRoutes.has(node.code) || airlinesInRoutes.has(node.id);
        }
        return true;
      });
    } else {
      // Full dataset - include all links
      filtered.links = [...(data.links || [])];
    }

    // Apply type filters
    filtered.nodes = filtered.nodes.filter(node => {
      if (node.label === 'Airport' && !showAirports) return false;
      if (node.label === 'Airline' && !showAirlines) return false;
      return true;
    });

    const nodeIds = new Set(filtered.nodes.map(n => n.id));
    
    filtered.links = (filtered.links || []).filter(link => {
      if (!showRoutes) return false;
      return nodeIds.has(link.source.id || link.source) && 
             nodeIds.has(link.target.id || link.target);
    });

    setFilteredGraphData(filtered);
  };

  // Update filters when dependencies change
  useEffect(() => {
    if (graphData && graphData.nodes && graphData.nodes.length > 0) {
      applyGraphFilters(graphData);
    }
  }, [showAirports, showAirlines, showRoutes, graphMode, response, currentDataset, graphData]);

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await axios.post(`${API}/graphrag/query`, { query });
      setResponse(res.data);
      
      // Check if the response has graph-worthy data (nodes/relationships)
      const hasGraphData = res.data.cypher || 
                          (res.data.results && res.data.results.length > 0 && 
                           res.data.results.some(r => typeof r === 'object' && Object.keys(r).length > 0));
      
      if (hasGraphData) {
        // Only switch to graph view if there's data to visualize
        toast.success('Consulta executada com sucesso! Veja o grafo na aba de visualização.');
        setGraphMode('query-results');
        setActiveTab('graph');
        loadGraphData();
      } else {
        // For simple text responses, stay on query tab
        toast.success('Consulta executada com sucesso!');
      }
    } catch (error) {
      console.error('Error executing query:', error);
      toast.error('Erro ao executar consulta: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFilterDataset = async (region = null) => {
    try {
      setLoading(true);
      
      // Set the dataset filter
      setCurrentDataset(region || 'full');
      setGraphMode('all');
      setResponse(null);
      
      // Always reload data to ensure we have fresh data
      await loadGraphData();
      
      if (region === 'BR') {
        toast.success('Exibindo apenas dados brasileiros');
      } else {
        toast.success('Exibindo todos os dados');
      }
    } catch (error) {
      console.error('Error filtering dataset:', error);
      toast.error('Erro ao filtrar dados');
    } finally {
      setLoading(false);
    }
  };  const handleSeedData = async (region = null) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/seed-data`, { 
        clear_existing: false,  // Never clear existing data
        region: region 
      });
      
      let message = `Dados carregados com sucesso!`;
      if (res.data.airports) {
        message = `${res.data.airports} aeroportos, ${res.data.airlines} companhias, ${res.data.routes} rotas`;
      }
      
      toast.success(message);
      setDataSeeded(true);
      setCurrentDataset(region || 'full');
      
      setGraphMode('all');
      setResponse(null);
      
      await loadGraphData();
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

  // Preset graph visualizations
  const loadPresetVisualization = async (preset) => {
    setLoading(true);
    try {
      let cypher = '';
      const isBrazil = currentDataset === 'BR';
      
      switch(preset) {
        case 'all-airports':
          // Show ALL airports from current dataset
          if (isBrazil) {
            cypher = "MATCH (a:Airport) WHERE a.country = 'BR' RETURN a";
          } else {
            cypher = "MATCH (a:Airport) RETURN a";
          }
          break;
        case 'major-hubs':
          // Show major airports (>10 connections) from current dataset
          if (isBrazil) {
            cypher = "MATCH (a:Airport)-[r:ROUTE]->() WHERE a.country = 'BR' WITH a, count(r) as connections WHERE connections > 10 RETURN a ORDER BY connections DESC";
          } else {
            cypher = "MATCH (a:Airport)-[r:ROUTE]->() WITH a, count(r) as connections WHERE connections > 10 RETURN a ORDER BY connections DESC";
          }
          break;
        case 'airlines':
          // Show ALL airlines from current dataset
          if (isBrazil) {
            cypher = "MATCH (al:Airline) WHERE al.country = 'BR' OR al.country = 'Brazil' RETURN al";
          } else {
            cypher = "MATCH (al:Airline) RETURN al";
          }
          break;
        default:
          return;
      }

      // Reset to 'all' mode to show full graph
      setGraphMode('all');
      setResponse(null);
      
      // Execute query to get data
      await axios.post(`${API}/query`, { query: cypher });
      
      
      // Reload graph data to show updated visualization
      await loadGraphData();
      setActiveTab('graph');
      
      toast.success('Visualização carregada!');
    } catch (error) {
      console.error('Error loading preset:', error);
      toast.error('Erro ao carregar visualização: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
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
                  Aero4jGraph <span className="text-cyan-400">Analytics</span>
                </h1>
                <p className="text-sm text-slate-400">Análise de Redes de Aviação com GraphRAG + Neo4j</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                onClick={() => handleFilterDataset('BR')}
                disabled={loading}
                className={`font-semibold rounded-md transition-all ${
                  currentDataset === 'BR' 
                    ? 'bg-green-600 text-white hover:bg-green-700 ring-2 ring-green-400' 
                    : 'bg-green-600/50 text-white hover:bg-green-600'
                }`}
                data-testid="filter-br-button"
              >
                <Database className="mr-2 h-4 w-4" />
                Dados Brasil
              </Button>
              <Button
                onClick={() => handleFilterDataset('full')}
                disabled={loading}
                className={`font-semibold rounded-md transition-all ${
                  currentDataset === 'full' 
                    ? 'bg-cyan-400 text-black hover:bg-cyan-500 shadow-[0_0_15px_-3px_rgba(34,211,238,0.4)] ring-2 ring-cyan-300' 
                    : 'bg-cyan-400/50 text-black hover:bg-cyan-400'
                }`}
                data-testid="seed-full-button"
              >
                <Database className="mr-2 h-4 w-4" />
                Dados Totais
              </Button>
            </div>
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
                      <table className="w-full text-sm text-left">
                        <thead className="text-xs text-cyan-400 uppercase bg-[#09090b] border-b border-[#27272a]">
                          <tr>
                            {Object.keys(response.results[0] || {}).map((key) => (
                              <th key={key} scope="col" className="px-6 py-3 font-semibold">
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {response.results.slice(0, 20).map((result, idx) => (
                            <tr key={idx} className="border-b border-[#27272a] hover:bg-[#27272a]/30 transition-colors">
                              {Object.keys(response.results[0] || {}).map((key) => (
                                <td key={key} className="px-6 py-4 text-slate-300">
                                  {typeof result[key] === 'object' && result[key] !== null
                                    ? Object.entries(result[key])
                                        .filter(([k, v]) => v !== null && v !== '' && String(v).toLowerCase() !== 'unknown')
                                        .map(([k, v]) => (
                                          <div key={k} className="mb-1">
                                            <span className="text-amber-400 text-xs">{k}:</span>{' '}
                                            <span className="text-slate-200">{String(v)}</span>
                                          </div>
                                        ))
                                    : result[key] !== null && result[key] !== '' && String(result[key]).toLowerCase() !== 'unknown'
                                    ? String(result[key])
                                    : '-'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {response.results.length > 20 && (
                        <p className="text-xs text-slate-500 mt-3 text-center">
                          Mostrando 20 de {response.results.length} resultados
                        </p>
                      )}
                    </div>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          {/* Graph Tab */}
          <TabsContent value="graph" data-testid="graph-content" className="space-y-4">
            {/* Controls and Stats Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Graph Mode Selector */}
              <Card className="bg-[#18181b] border-[#27272a] p-4">
                <h3 className="text-sm font-semibold mb-3 text-cyan-400">Modo de Visualização</h3>
                <div className="space-y-2">
                  <Button
                    onClick={() => setGraphMode('all')}
                    variant={graphMode === 'all' ? 'default' : 'outline'}
                    className={`w-full justify-start ${graphMode === 'all' ? 'bg-cyan-600' : 'border-gray-600'}`}
                  >
                    🌐 Grafo Completo
                  </Button>
                  <Button
                    onClick={() => setGraphMode('query-results')}
                    variant={graphMode === 'query-results' ? 'default' : 'outline'}
                    className={`w-full justify-start ${graphMode === 'query-results' ? 'bg-cyan-600' : 'border-gray-600'}`}
                    disabled={!response}
                  >
                    🔍 Resultados da Busca
                  </Button>
                </div>
              </Card>

              {/* Filters */}
              <Card className="bg-[#18181b] border-[#27272a] p-4">
                <h3 className="text-sm font-semibold mb-3 text-cyan-400">Filtros</h3>
                <div className="space-y-2">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showAirports}
                      onChange={(e) => setShowAirports(e.target.checked)}
                      className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-cyan-600"
                    />
                    <span className="text-sm text-slate-300">✈️ Aeroportos</span>
                  </label>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showAirlines}
                      onChange={(e) => setShowAirlines(e.target.checked)}
                      className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-amber-600"
                    />
                    <span className="text-sm text-slate-300">🛫 Companhias Aéreas</span>
                  </label>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showRoutes}
                      onChange={(e) => setShowRoutes(e.target.checked)}
                      className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-cyan-600"
                    />
                    <span className="text-sm text-slate-300">🔗 Rotas</span>
                  </label>
                </div>
              </Card>

              {/* Statistics */}
              <Card className="bg-[#18181b] border-[#27272a] p-4">
                <h3 className="text-sm font-semibold mb-3 text-cyan-400">Estatísticas</h3>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Nós:</span>
                    <span className="text-cyan-400 font-semibold">{filteredGraphData.nodes.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Relacionamentos:</span>
                    <span className="text-cyan-400 font-semibold">{filteredGraphData.links.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Aeroportos:</span>
                    <span className="text-cyan-400 font-semibold">
                      {filteredGraphData.nodes.filter(n => n.label === 'Airport').length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Companhias:</span>
                    <span className="text-amber-400 font-semibold">
                      {filteredGraphData.nodes.filter(n => n.label === 'Airline').length}
                    </span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Preset Visualizations */}
            <Card className="bg-[#18181b] border-[#27272a] p-4">
              <h3 className="text-sm font-semibold mb-3 text-cyan-400">Visualizações Pré-definidas</h3>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  onClick={() => loadPresetVisualization('all-airports')}
                  disabled={loading}
                  variant="outline"
                  className="border-green-600 text-green-400 hover:bg-green-900/20"
                >
                  ✈️ Aeroportos
                </Button>
                <Button
                  onClick={() => loadPresetVisualization('major-hubs')}
                  disabled={loading}
                  variant="outline"
                  className="border-purple-600 text-purple-400 hover:bg-purple-900/20"
                >
                  🏢 Grandes Hubs
                </Button>
                <Button
                  onClick={() => loadPresetVisualization('airlines')}
                  disabled={loading}
                  variant="outline"
                  className="border-amber-600 text-amber-400 hover:bg-amber-900/20"
                >
                  🛫 Companhias
                </Button>
              </div>
            </Card>

            {/* Graph Visualization */}
            <Card className="bg-[#18181b] border-[#27272a] p-6">
              <h2 className="text-xl font-semibold mb-4 text-cyan-400" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Rede de Aviação - Grafo Interativo
              </h2>
              <div className="network-graph-container" style={{ height: '600px' }} data-testid="graph-visualization">
                {filteredGraphData.nodes.length > 0 ? (
                  <ForceGraph2D
                    graphData={filteredGraphData}
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
                    <p className="text-slate-400">Carregue os dados ou faça uma busca para visualizar o grafo</p>
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