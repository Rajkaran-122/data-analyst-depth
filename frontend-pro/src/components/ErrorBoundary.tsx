import { Component, ReactNode, ErrorInfo } from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

interface ErrorBoundaryProps {
    children: ReactNode;
    fallback?: ReactNode;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
        return { hasError: true };
    }

    componentDidCatch(_error: Error, errorInfo: ErrorInfo) {
        console.error('Error Boundary caught an error:', _error, errorInfo);

        this.setState({
            error: _error,
            errorInfo,
        });

        // Send to error tracking service (e.g., Sentry)
        // if (window.Sentry) {
        //   window.Sentry.captureException(_error, { extra: errorInfo });
        // }
    }

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        });
    };

    handleGoHome = () => {
        window.location.href = '/';
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-screen flex items-center justify-center p-4 bg-background">
                    <Card className="w-full max-w-lg">
                        <CardHeader>
                            <div className="flex items-center gap-2 text-destructive">
                                <AlertCircle className="h-5 w-5" />
                                <CardTitle>Something went wrong</CardTitle>
                            </div>
                            <CardDescription>
                                An unexpected error occurred in the application
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {this.state.error && (
                                <div className="rounded-md bg-destructive/10 p-4">
                                    <p className="text-sm font-medium text-destructive mb-2">
                                        Error Message:
                                    </p>
                                    <code className="text-xs">{this.state.error.toString()}</code>
                                </div>
                            )}

                            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                                <details className="rounded-md bg-muted p-4">
                                    <summary className="text-sm font-medium cursor-pointer">
                                        Stack Trace (Development Only)
                                    </summary>
                                    <pre className="mt-2 text-xs overflow-auto">
                                        {this.state.errorInfo.componentStack}
                                    </pre>
                                </details>
                            )}
                        </CardContent>
                        <CardFooter className="flex gap-2">
                            <Button onClick={this.handleReset} variant="outline" className="flex-1">
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Try Again
                            </Button>
                            <Button onClick={this.handleGoHome} className="flex-1">
                                <Home className="mr-2 h-4 w-4" />
                                Go Home
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}

// Error Fallback for Suspense boundaries
export function ErrorFallback({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary?: () => void }) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-4">
            <AlertCircle className="h-12 w-12 text-destructive mb-4" />
            <h2 className="text-lg font-semibold mb-2">Oops! Something went wrong</h2>
            <p className="text-sm text-muted-foreground mb-4 text-center max-w-md">
                {error.message || 'An unexpected error occurred'}
            </p>
            {resetErrorBoundary && (
                <Button onClick={resetErrorBoundary}>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Try again
                </Button>
            )}
        </div>
    );
}
