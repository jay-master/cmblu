% Impedanzspektroskopie von Hand

close all
clear

I_DC=[-12,-3,3,12];%(-10.5:6:14.5);
deltaI=1;

isinus=0.01;
exponent=[-3, 4];
freqstep=6;

frequency=10.^(exponent(1):(1/freqstep):exponent(end));
omega=2*pi*ones(length(I_DC),1)*frequency;

R1=0.05e-3;
R2=0.05e-3;
L = 1e-8;
U0=0;
pR=[0.4, 4];
F = 96487;
R = 8.3145;
T=298;
pPb=0.5;
pH2SO4=0.004;
Cdl=6000;
D_Pb=1e-11;
d_diff=1e-4;
% positive electrode = 1, negative electrode = -1
electrode=1;

conc_f=1;
conc_SO=1;
Q_diff=0;

U_table=-0.1:0.0001:0.1;
I_calc=pR(2)*electrode * (exp(pR(1)*2*F/R/T*U_table)-exp(-(1-pR(1))*2*F/R/T*U_table));
R_table=electrode*U_table./I_calc;
I_table=I_calc;
index=find(I_table==0);
I_table(index)=[];
U_table(index)=[];
R_table(index)=[];

c_P=c_Pbp(pPb, I_table);
c_H=c_H2SO4p(pH2SO4, I_table);
    if electrode ==1
        c1=c_P;
        c2=c_H;
    elseif electrode == -1
        c2=c_P;
        c1=c_H;
    end
        

% Berechnung der Strom- und Frequenzabhängigen Konzentration
conc_Pb=zeros(length(frequency), length(I_DC));
conc_SO4=zeros(length(frequency), length(I_DC));
for fi=0:length(frequency)-1
    f=frequency(end-fi); % Frequenzen von der höchsten zur niedrigsten
    
    Q_cum=max(1,3./f)*I_DC/2/F;
    Q_diff_Pb=1e-11*1e14*1e-7*4*pi*max(1,3./f)*(conc_f-1);
    Q_diff_SO=1e-9/1e-6*max(1,3./f)*(conc_SO-1)*1;
    conc_f=min(2,max(1e-1,(conc_f-Q_cum*1-Q_diff_Pb)));
    conc_SO=min(2,max(1e-1,(conc_SO+Q_cum*1.56/10/0.5-Q_diff_SO*0.5^1.5)));
    
    conc_Pb(end-fi,:)=conc_f;
    conc_SO4(end-fi,:)=conc_SO;
end

n_per_min=3;
fft_per=1; % über wieviele Perioden geht die FFT?
U_RC0=0;
I_R0=0;
r_limit=pR(2)*2;
c0Pb=1;

U_RCo=zeros(length(frequency), length(I_DC));
I_RCo=zeros(length(frequency), length(I_DC));
I_Ro=zeros(length(frequency), length(I_DC));
ReZlin=zeros(length(frequency), length(I_DC));
ImZlin=zeros(length(frequency), length(I_DC));
ReZo=zeros(length(frequency), length(I_DC));
ImZo=zeros(length(frequency), length(I_DC));
for n=1:length(I_DC)
    Q_diff=0;
    
    I=I_DC(n);
    f=1e-3;
    
    conc_f=conc_Pb(1,n);
    conc_SO=conc_SO4(1,n);
    
    sample=2^5;
    fft_sample=sample*fft_per;
    t_end=(n_per_min-fft_per)/f-1/(sample*f);
    isin=0;
    U_RC0=interp1(I_table, U_table,I);
    for erste=1
        sim('EIS_Blei_pos_Konz');

        U_RC0=U_RC(end);
        I_R0=I_R(end);
    end

    isin=isinus;
    ReZlin_dummy = zeros(1,length(frequency));
    ImZlin_dummy = zeros(1,length(frequency));
    ReZo_dummy = zeros(1,length(frequency));
    ImZo_dummy = zeros(1,length(frequency));
    for fi=1:length(frequency)
        sample=2^5;
        fft_sample=sample*fft_per;
        f=frequency(fi);
        n_per=n_per_min;
        t_end=n_per/f-1/(sample*f);

        conc_f=conc_Pb(fi,n);
        conc_SO=conc_SO4(fi,n);

        for schleife=1
        sim('EIS_Blei_pos_Konz');

        
        % Driftkorrektur
        drift=(voltage(sample)-voltage(end))/(t_end-1/f+1/(sample*f)); % das ist die Steigung
        t_drift=0:1/(sample*f):(fft_per/f-1/(sample*f));
                
        u_total=voltage((end-fft_sample+1):end)+t_drift'*drift*sign(I);
        
        iRC=I_RC((end-fft_sample+1):end);
        iR=I_R((end-fft_sample+1):end);
        u_RCo=U_RC((end-fft_sample+1):end);
        
        N=length(u_total);
        
        Flinear = fft(u_total,N)*2/N; % FFT Analyse des Eingangsstroms, schon normiert auf die Anzahl der Samples
        FRC = fft(iRC,N)*2/N; % FFT Analyse des Eingangsstroms, schon normiert auf die Anzahl der Samples
        FR = fft(iR,N)*2/N; % FFT Analyse des Eingangsstroms, schon normiert auf die Anzahl der Samples
        F_RCo=fft(u_RCo,N)*2/N;

        I_RCo(fi,n)=iRC(end);
        I_Ro(fi,n)=iR(end);
        U_RCo(fi,n)=u_RCo(end);
        
        % Hier kommt nun die Impedanzberechnung
        fsoll = round(f*N/sample/f)+1; % Die Eingangsfrequenz
        Zlin = Flinear(fsoll) ./ isin/(-1i); % Impedanz, so wie sie sein sollte
        Zo = F_RCo(fsoll) ./ FRC(fsoll);
    
        U_RC0=u_RCo(end);
        I_R0=iRC(end);
        end
        ReZlin_dummy(fi) = real(Zlin);
        ImZlin_dummy(fi) = imag(Zlin);
        ReZo_dummy(fi) = real(Zo);
        ImZo_dummy(fi) = imag(Zo);
        
   end
    figure; plot(ReZlin_dummy, -ImZlin_dummy, ReZlin_dummy(1), -ImZlin_dummy(1), 'ro');
    title('komplett');
    ReZlin(:,n) = ReZlin_dummy;
    ImZlin(:,n) = ImZlin_dummy;
    ReZo(:,n) = ReZo_dummy;
    ImZo(:,n) = ImZo_dummy;
    
    figure; subplot(2,1,1);semilogx(frequency, sqrt(ReZlin_dummy.^2+ImZlin_dummy.^2));
    subplot(2,1,2);semilogx(frequency, atan(ImZlin_dummy./ReZlin_dummy));
end    

% Überprüfung mit zhit
for j=1:length(I_DC)
    z = ReZlin(:,j)+1i*ImZlin(:,j);
    absz = abs(z);
    phiz = angle(z);           
    abszhit=zhit(frequency',absz,phiz);
    
    if abs(abszhit-absz)>5e-5
        disp('Fehler: Zhit nicht konsistent');
    end
    
    figure; semilogx(frequency,absz*1000,'k.',frequency,abszhit*1000,'ro',frequency,(absz-abszhit)*1000,'bx');
    set(gca, 'Fontsize', 16, 'Fontname', 'Arial');
    line([1e-3 1e4],[0 0],'Color',[0 0 0]);
    legend('simulation','Z-HIT reconstruction','difference');
    xlabel('{\itf} / Hz');
    ylabel('|{\itZ}({\it\omega})| / m\Omega');
    grid on;
end

    h=figure;
    set(gcf,'Units','normalized');
    set(0,'Units','normalized');
    a = get(0,'ScreenSize');
    set(h, 'Position',[a(1)+0.1 a(2)+0.03 a(3)-0.2 a(4)-0.1]);
 
    plot(ReZlin*1000, ImZlin*1000, 'Linewidth',6);
    set(gca,'YDir','reverse', 'Fontsize', 30, 'Fontname', 'Arial')
    xlabel('Re({\itZ}({\it\omega})) / m\Omega');
    ylabel('Im({\itZ}({\it\omega})) / m\Omega')
    grid on;
    % Skalierung anpassen
    hoehe_Spektrum=max(max(ImZlin))-min(min(ImZlin));
    breite_Spektrum=max(max(ReZlin))-min(min(ReZlin));
 
    if hoehe_Spektrum > breite_Spektrum
       limits = get(gca,'YLim');
       set(gca,'XLim',[max(max(ReZlin))*1000-(limits(2)-limits(1)) max(max(ReZlin))*1000]);
    else
       limits = get(gca,'XLim');
       set(gca,'YLim',[-(limits(2)-limits(1))/2 (limits(2)-limits(1))/2]);
    end;
    legend('-4 {\itI}_2_0', '-1 {\itI}_2_0','1 {\itI}_2_0','4 {\itI}_2_0');
