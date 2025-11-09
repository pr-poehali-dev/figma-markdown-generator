import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import Icon from '@/components/ui/icon';

interface UIElement {
  id: number;
  type: string;
  name: string;
  description: string;
  logic: string;
}

const Index = () => {
  const [figmaUrl, setFigmaUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [markdown, setMarkdown] = useState('');
  const [elements, setElements] = useState<UIElement[]>([]);
  const { toast } = useToast();

  const generateMockElements = (url: string): UIElement[] => {
    const mockElements: UIElement[] = [
      {
        id: 1,
        type: 'button',
        name: 'primary_btn',
        description: 'Primary button с градиентом',
        logic: 'При нажатии выполняет основное действие'
      },
      {
        id: 2,
        type: 'input',
        name: 'email_field',
        description: 'Текстовое поле для email',
        logic: 'Валидация email формата при вводе'
      },
      {
        id: 3,
        type: 'text',
        name: 'welcome_heading',
        description: 'Заголовок "Добро пожаловать"',
        logic: 'Статический текст для приветствия'
      },
      {
        id: 4,
        type: 'card',
        name: 'info_card',
        description: 'Карточка с информацией',
        logic: 'Отображение дополнительных данных'
      },
      {
        id: 5,
        type: 'icon',
        name: 'menu_icon',
        description: 'Иконка меню-бургера',
        logic: 'Открытие боковой навигации'
      }
    ];
    
    return mockElements;
  };

  const generateMarkdown = (elements: UIElement[], frameName: string): string => {
    let md = `# ${frameName} Documentation\n\n`;
    md += `| № | Тип элемента | Название | Описание | Логика работы |\n`;
    md += `|---|--------------|----------|-----------|---------------|\n`;
    
    elements.forEach((element) => {
      md += `| ${element.id} | ${element.type} | ${element.name} | ${element.description} | ${element.logic} |\n`;
    });
    
    return md;
  };

  const handleGenerate = async () => {
    if (!figmaUrl.trim()) {
      toast({
        title: 'Ошибка',
        description: 'Пожалуйста, введите ссылку на Figma Frame',
        variant: 'destructive'
      });
      return;
    }

    setIsLoading(true);
    
    setTimeout(() => {
      const mockElements = generateMockElements(figmaUrl);
      setElements(mockElements);
      
      const frameName = 'Login Screen';
      const md = generateMarkdown(mockElements, frameName);
      setMarkdown(md);
      
      setIsLoading(false);
      
      toast({
        title: '✅ Готово!',
        description: `Создана документация для ${mockElements.length} элементов`
      });
    }, 1500);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    toast({
      title: 'Скопировано!',
      description: 'Markdown скопирован в буфер обмена'
    });
  };

  const handleClear = () => {
    setFigmaUrl('');
    setMarkdown('');
    setElements([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-cyan-50 to-blue-50">
      <div className="container max-w-5xl mx-auto px-4 py-12">
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full mb-4">
            <Icon name="FileText" size={20} className="text-primary" />
            <span className="text-sm font-medium text-primary">Figma to Markdown</span>
          </div>
          
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-violet-600 to-cyan-600 bg-clip-text text-transparent">
            Генератор документации
          </h1>
          
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Превратите Figma Frame в красивую Markdown-документацию для вашей команды за секунды
          </p>
        </div>

        <Card className="mb-8 shadow-xl border-0 animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="Link" size={24} className="text-primary" />
              Вставьте ссылку на Figma Frame
            </CardTitle>
            <CardDescription>
              Поддерживаются ссылки формата: figma.com/file/FILE_KEY/...?node-id=NODE_ID
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Input
                placeholder="https://www.figma.com/file/..."
                value={figmaUrl}
                onChange={(e) => setFigmaUrl(e.target.value)}
                className="flex-1 h-12 text-base"
                disabled={isLoading}
              />
              <Button
                onClick={handleGenerate}
                disabled={isLoading}
                size="lg"
                className="bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-700 hover:to-cyan-700 px-8"
              >
                {isLoading ? (
                  <>
                    <Icon name="Loader2" size={20} className="mr-2 animate-spin" />
                    Генерация...
                  </>
                ) : (
                  <>
                    <Icon name="Sparkles" size={20} className="mr-2" />
                    Генерировать
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {markdown && (
          <Card className="shadow-xl border-0 animate-scale-in">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Icon name="FileCode" size={24} className="text-primary" />
                  Результат
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleClear}
                    className="gap-2"
                  >
                    <Icon name="RotateCcw" size={16} />
                    Очистить
                  </Button>
                  <Button
                    onClick={handleCopy}
                    size="sm"
                    className="gap-2 bg-primary hover:bg-primary/90"
                  >
                    <Icon name="Copy" size={16} />
                    Копировать
                  </Button>
                </div>
              </div>
              <CardDescription>
                Найдено элементов: {elements.length}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-slate-900 rounded-lg p-6 overflow-x-auto">
                <pre className="text-sm text-slate-50 font-mono whitespace-pre-wrap">
                  {markdown}
                </pre>
              </div>

              <div className="mt-6 p-4 bg-violet-50 rounded-lg border border-violet-200">
                <div className="flex items-start gap-3">
                  <Icon name="Info" size={20} className="text-violet-600 mt-0.5" />
                  <div className="text-sm text-violet-900">
                    <p className="font-medium mb-1">Готово к использованию!</p>
                    <p className="text-violet-700">
                      Скопируйте Markdown и вставьте в Confluence, Notion или любую документацию
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {!markdown && (
          <div className="grid md:grid-cols-3 gap-6 animate-fade-in">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-violet-100 rounded-lg flex items-center justify-center mb-3">
                  <Icon name="Zap" size={24} className="text-violet-600" />
                </div>
                <CardTitle className="text-xl">Мгновенно</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Получите готовую документацию за несколько секунд
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-cyan-100 rounded-lg flex items-center justify-center mb-3">
                  <Icon name="Table" size={24} className="text-cyan-600" />
                </div>
                <CardTitle className="text-xl">Структурно</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Все элементы в удобной таблице с пронумерованными позициями
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                  <Icon name="CheckCircle" size={24} className="text-blue-600" />
                </div>
                <CardTitle className="text-xl">Готово к работе</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Совместимость с Confluence, Notion, GitHub
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
